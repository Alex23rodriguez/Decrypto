from fastapi import APIRouter, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates/lobby")


# In-memory storage for game players (game_id -> set of player names)
Games: dict[str, dict[WebSocket, str | None]] = {}


def get_current_players(game_id):
    return [name for name in Games.get(game_id, {}).values() if name]


@router.get("/game/{game_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, game_id: str):
    # Get current players in the game
    current_players = get_current_players(game_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "game_id": game_id,
            "current_players": current_players,
            "name_taken": False,
        },
    )


@router.websocket("/ws/game/{game_id}")
async def handle_websocket(websocket: WebSocket, game_id: str):
    await websocket.accept()

    await connect(websocket, game_id)
    try:
        # Keep connection alive
        while True:
            # Wait for any message (we don't expect client messages for now)
            action = await websocket.receive_json()
            print("Recieved action")
            print(action)
            if action["action"] == "join":
                await join_game(websocket, game_id, action["player_name"])

            elif action["action"] == "leave":
                await leave_game(websocket, game_id)

    except WebSocketDisconnect:
        await disconnect(websocket, game_id)


async def join_game(ws: WebSocket, game_id: str, player_name: str = Form(...)):
    if player_name not in Games[game_id].values():
        Games[game_id][ws] = player_name
        print(player_name, "joined game", game_id)
        # Broadcast updated player list
        await broadcast_player_list(game_id)

        text = templates.env.get_template("joined.html").render(
            {
                "game_id": game_id,
                "player_name": player_name,
            }
        )
        await ws.send_text(text)
    else:
        print(f"name {player_name} exists")
        await ws.send_text(
            templates.env.get_template("form.html").render(
                {"name_taken": True, "game_id": game_id}
            )
        )


async def leave_game(ws: WebSocket, game_id: str):
    Games[game_id][ws] = None

    # Broadcast updated player list
    await broadcast_player_list(game_id)

    # Return the input form
    await ws.send_text(
        templates.env.get_template("form.html").render(
            {"game_id": game_id},
        )
    )


async def connect(ws: WebSocket, game_id: str):
    if game_id not in Games:
        Games[game_id] = {}
    Games[game_id][ws] = None

    print(f"new websocket: {ws}")

    # Send initial player list
    current_players = get_current_players(game_id)
    await ws.send_text(
        templates.env.get_template("player_list.html").render(
            {"current_players": current_players}
        )
    )


async def disconnect(ws: WebSocket, game_id: str):
    # Remove connection on disconnect
    del Games[game_id][ws]

    await broadcast_player_list(game_id)

    if not Games[game_id]:
        del Games[game_id]


async def broadcast_player_list(game_id: str):
    """Broadcast the current player list to all connected clients for a game."""
    current_players = get_current_players(game_id)
    print(f"current players in {game_id}: {current_players}")
    for ws, player_name in Games[game_id].items():
        text = templates.env.get_template("player_list.html").render(
            {"current_players": current_players, "player_name": player_name}
        )
        await ws.send_text(text)
