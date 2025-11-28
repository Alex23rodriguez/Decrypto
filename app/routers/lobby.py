from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.storage import MIN_NUM_PLAYERS, get_lobby_storage

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

    player_id = lobby.add_player(room_id, ws)

    # Connect
    await ws.accept(
        headers=[
            (
                b"Set-Cookie",
                f"player_token={player_id}; path=/; max-age=7200; SameSite=Strict".encode(
                    "utf8"
                ),
            )
        ]
    )
    ws.cookies["player_token"] = player_id

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
    ready_players = lobby.get_ready_players(room_id)

    await ws.send_text(
        templates.env.get_template("player_list.html").render(
            {"ready_players": ready_players, "min_players": MIN_NUM_PLAYERS}
        )
    )


async def disconnect_player(ws: WebSocket, room_id: str):
    """Handle a player leaving a room."""
    lobby.remove_player(room_id, ws)

    await broadcast_new_ready_players_list(room_id)


async def handle_action(action: dict, ws: WebSocket, room_id: str):
    print("action:", action)
    if action["action"] == "join":
        await handle_player_joined(ws, room_id, name=action.get("player_name", None))

    elif action["action"] == "leave":
        await handle_player_not_ready(ws, room_id)

    elif action["action"] == "start_game":
        player_id = await get_player_id(ws)
        if lobby.can_start_game(room_id, player_id):
            await start_game(room_id)


async def get_player_id(ws: WebSocket):
    player_id = ws.cookies.get("player_token")
    assert player_id
    print(f"got '{player_id}' on get_player_id")
    return player_id


async def broadcast_new_ready_players_list(room_id: str):
    """Broadcast the ready player list to all connected clients for a room."""
    ready_players = lobby.get_ready_players(room_id)
    template = templates.env.get_template("player_list.html")

    await lobby.broadcast_message(
        room_id,
        lambda p: template.render(
            {
                "ready_players": ready_players,
                "player_name": p.name,
                "min_players": MIN_NUM_PLAYERS,
            }
        ),
    )


async def handle_player_joined(ws: WebSocket, room_id: str, name: str | None):
    """Handle a player choosing a name. Fails if name invalid"""
    updated = lobby.update_player_name(room_id, ws, name)

    if updated:
        updated = lobby.update_player_ready(room_id, ws, True)
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


async def handle_player_not_ready(ws: WebSocket, room_id: str):
    """Handle a player no longer being ready."""
    lobby.update_player_ready(room_id, ws, False)

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
