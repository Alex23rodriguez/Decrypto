import secrets
from pprint import pprint

from fastapi import APIRouter, Form, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.storage import get_lobby_storage


router = APIRouter()
templates = Jinja2Templates(directory="app/templates/lobby")
lobby = get_lobby_storage()


# ROUTES


@router.get("/lobby", response_class=RedirectResponse)
async def redirect_to_room(room_id: str):
    return RedirectResponse(url=f"/lobby/{room_id}", status_code=302)


@router.get("/lobby/{room_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, room_id: str):
    # Get current players in the lobby
    ready_players = lobby.get_ready_players(room_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_id": room_id,
            "ready_players": ready_players,
            "name_taken": False,
        },
    )


@router.get("/lobby", response_class=HTMLResponse)
async def get_lobby():
    return RedirectResponse(url="/", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@router.websocket("/ws/lobby/{room_id}")
async def handle_websocket(ws: WebSocket, room_id: str):
    """Websocket lifecycle. Main loop for each client"""

    # Connect
    await ws.accept()

    await connect_player(ws, room_id)

    # Lifecycle
    try:
        while True:
            action: dict = await ws.receive_json()
            await handle_action(action, ws, room_id)

    # Disconnect
    except WebSocketDisconnect:
        await disconnect_player(ws, room_id)


# UTILS


async def connect_player(ws: WebSocket, room_id: str):
    """Handle a player joining a room."""
    player_id = lobby.add_player(room_id, ws)
    ready_players = lobby.get_ready_players(room_id)

    await ws.send_text(
        templates.env.get_template("player_list.html").render(
            {"ready_players": ready_players}
        )
    )
    await refresh_player_id(ws, player_id)


async def refresh_player_id(ws, player_id):
    await ws.send_json(
        {
            "type": "update-player-token",
            "player_token": player_id,
        }
    )


async def disconnect_player(ws: WebSocket, room_id: str):
    """Handle a player leaving a room."""
    player_id = ws.cookies.get("player_token")
    if not player_id:
        player_id = lobby.add_player(room_id, ws)  # will give existing id

    lobby.remove_player(room_id, player_id)

    await broadcast_new_ready_players_list(room_id)


async def handle_action(action: dict, ws: WebSocket, room_id: str):
    print("action:", action)
    if action["action"] == "join":
        await handle_player_joined(ws, room_id, name=action.get("player_name", None))

    elif action["action"] == "leave":
        await handle_player_left(ws, room_id)

    elif action["action"] == "start_game":
        player_id = await get_player_id(room_id, ws)
        if lobby.can_start_game(room_id, player_id):
            await start_game(room_id)


async def get_player_id(room_id, ws: WebSocket):
    player_id = ws.cookies.get("player_token")
    if not player_id:
        player_id = lobby.add_player(room_id, ws)
        await refresh_player_id(ws, player_id)
    return player_id


async def broadcast_new_ready_players_list(room_id: str):
    """Broadcast the ready player list to all connected clients for a room."""
    ready_players = lobby.get_ready_players(room_id)
    template = templates.env.get_template("player_list.html")

    await lobby.broadcast_message(
        room_id,
        lambda p: template.render(
            {"ready_players": ready_players, "player_name": p.name}
        ),
    )


async def handle_player_joined(ws: WebSocket, room_id: str, name: str | None):
    """Handle a player choosing a name. Fails if name invalid"""

    player_id = await get_player_id(room_id, ws)
    updated = lobby.update_player_name(room_id, player_id, name)

    if updated:
        # Broadcast updated player list
        await broadcast_new_ready_players_list(room_id)

        text = templates.env.get_template("joined.html").render(
            {
                "room_id": room_id,
                "player_name": name,
            }
        )
        await ws.send_text(text)
    else:
        await ws.send_text(
            templates.env.get_template("form.html").render(
                {"name_taken": True, "room_id": room_id}
            )
        )


async def handle_player_left(ws: WebSocket, room_id: str):
    """Handle a player no longer being ready."""
    lobby.remove_player(room_id, await get_player_id(room_id, ws))

    # Broadcast updated player list
    await broadcast_new_ready_players_list(room_id)

    # Return the input form
    await ws.send_text(
        templates.env.get_template("form.html").render(
            {"room_id": room_id},
        )
    )


async def start_game(room_id: str):
    players_in_game = lobby.start_game(room_id)

    for p in players_in_game:
        await p.ws.send_json(
            {
                "type": "game-started",
                "url": f"/game/{room_id}",
            }
        )
