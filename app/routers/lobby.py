import secrets

from fastapi import (APIRouter, Form, Request, WebSocket, WebSocketDisconnect,
                     status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates/lobby")
MIN_NUM_PLAYERS = 1


@router.get("/lobby/", response_class=RedirectResponse)
async def redirect_to_room(room_id: str):
    return RedirectResponse(url=f"/lobby/{room_id}", status_code=302)


# In-memory storage for lobby players
# (room_id -> websocket -> Optional[player_name])
Rooms: dict[str, dict[WebSocket, str | None]] = {}
Games: dict[str, dict[str, str]] = {}


def get_ready_players(room_id) -> list[str]:
    """Get players that have already chosen a name for a room."""
    return [name for name in Rooms.get(room_id, {}).values() if name]


def can_start_game(room_id: str, ws: WebSocket):
    return Rooms[room_id][ws] and len(get_ready_players(room_id)) >= MIN_NUM_PLAYERS


async def broadcast_read_player_list(room_id: str):
    """Broadcast the ready player list to all connected clients for a room."""
    current_players = get_ready_players(room_id)
    for ws, player_name in Rooms[room_id].items():
        text = templates.env.get_template("player_list.html").render(
            {"current_players": current_players, "player_name": player_name}
        )
        await ws.send_text(text)


@router.get("/lobby/{room_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, room_id: str):
    # Get current players in the lobby
    current_players = get_ready_players(room_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_id": room_id,
            "current_players": current_players,
            "name_taken": False,
        },
    )


@router.get("/lobby", response_class=HTMLResponse)
async def get_lobby():
    return RedirectResponse(url="/", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@router.websocket("/ws/lobby/{room_id}")
async def handle_websocket(websocket: WebSocket, room_id: str):
    """Websocket lifecycle. Main loop for each client"""
    await websocket.accept()

    await connect_player(websocket, room_id)
    try:
        # Keep connection alive
        while True:
            # Wait for any message (we don't expect client messages for now)
            action = await websocket.receive_json()
            print("action:", action)
            if action["action"] == "join":
                await update_player_status_ready(
                    websocket, room_id, action["player_name"]
                )

            elif action["action"] == "leave":
                await update_player_status_not_ready(websocket, room_id)

            elif action["action"] == "start_game":
                if can_start_game(room_id, websocket):
                    await redirect_ready_players_to_game(room_id)

    except WebSocketDisconnect:
        await disconnect_player(websocket, room_id)


async def connect_player(ws: WebSocket, room_id: str):
    """Handle a player joining a room."""
    if room_id not in Rooms:
        Rooms[room_id] = {}
    Rooms[room_id][ws] = None

    # Send initial player list
    current_players = get_ready_players(room_id)
    await ws.send_text(
        templates.env.get_template("player_list.html").render(
            {"current_players": current_players}
        )
    )


async def disconnect_player(ws: WebSocket, room_id: str):
    """Handle a player leaving a room."""
    # Remove connection on disconnect
    del Rooms[room_id][ws]

    await broadcast_read_player_list(room_id)

    if not Rooms[room_id]:
        del Rooms[room_id]


def is_valid_name(name: str, room_id):
    if len(name.strip()) > 64:
        return False

    if name in get_ready_players(room_id):
        return False

    return True


async def update_player_status_ready(
    ws: WebSocket, room_id: str, player_name: str = Form(...)
):
    """Handle a player choosing a name. Fails if name invalid"""
    if is_valid_name(player_name, room_id):
        Rooms[room_id][ws] = player_name
        # Broadcast updated player list
        await broadcast_read_player_list(room_id)

        text = templates.env.get_template("joined.html").render(
            {
                "room_id": room_id,
                "player_name": player_name,
            }
        )
        await ws.send_text(text)

    else:
        await ws.send_text(
            templates.env.get_template("form.html").render(
                {"name_taken": True, "room_id": room_id}
            )
        )


async def update_player_status_not_ready(ws: WebSocket, room_id: str):
    """Handle a player no longer being ready."""
    Rooms[room_id][ws] = None

    # Broadcast updated player list
    await broadcast_read_player_list(room_id)

    # Return the input form
    await ws.send_text(
        templates.env.get_template("form.html").render(
            {"room_id": room_id},
        )
    )


async def redirect_ready_players_to_game(room_id: str):
    game_players: dict[str, str] = {}
    for ws, player_name in Rooms[room_id].items():
        if player_name:
            player_token = secrets.token_urlsafe(32)
            game_players[player_token] = player_name
            print(f"gave {player_name} token: {player_token}")

            await ws.send_json(
                {
                    "type": "game-started",
                    "url": f"/game/{room_id}",
                    "player_token": player_token,
                }
            )
    Games[room_id] = game_players
