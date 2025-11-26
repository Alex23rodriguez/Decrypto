from fastapi import APIRouter, Form, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates/lobby")

# In-memory storage for game players (game_id -> set of player names)
game_players = {}

# WebSocket connections (game_id -> set of WebSocket connections)
game_connections = {}


@router.get("/game/{game_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, game_id: str):
    # Get current players in the game
    current_players = list(game_players.get(game_id, set()))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "game_id": game_id,
            "current_players": current_players,
            "name_taken": False,
        },
    )


@router.post("/game/{game_id}/join", response_class=HTMLResponse)
async def join_game(request: Request, game_id: str, player_name: str = Form(...)):
    if game_id not in game_players:
        game_players[game_id] = set()

    # Add player to the game
    if player_name not in game_players[game_id]:
        game_players[game_id].add(player_name)

        # Broadcast updated player list
        await broadcast_player_list(game_id)

        # Get other players (excluding current player)
        other_players = game_players[game_id] - {player_name}

        return templates.TemplateResponse(
            "joined.html",
            {
                "request": request,
                "game_id": game_id,
                "player_name": player_name,
                "other_players": list(other_players),
            },
        )

    else:
        return templates.TemplateResponse(
            "form.html",
            {"request": request, "name_taken": True, "game_id": game_id},
        )


@router.post("/game/{game_id}/leave", response_class=HTMLResponse)
async def leave_game(request: Request, game_id: str, player_name: str = Form(...)):
    # Remove player from the game
    if game_id in game_players:
        game_players[game_id].discard(player_name)

    # Broadcast updated player list
    await broadcast_player_list(game_id)

    # Return the input form
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "name_taken": False, "game_id": game_id},
    )


@router.get("/game/{game_id}/validate-name", response_class=HTMLResponse)
async def validate_name(request: Request, game_id: str, name: str):
    # Trim whitespace and check if name is available
    name = name.strip()
    current_players = game_players.get(game_id, set())
    available = name not in current_players and len(name) > 0

    return templates.TemplateResponse(
        "game_validate_name.html",
        {
            "request": request,
            "available": available,
            "message": "Name already taken" if not available and len(name) > 0 else "",
        },
    )


@router.websocket("/ws/game/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str):
    await websocket.accept()

    # Add connection to the game
    if game_id not in game_connections:
        game_connections[game_id] = set()
    game_connections[game_id].add(websocket)

    try:
        # Send initial player list
        current_players = list(game_players.get(game_id, set()))
        await websocket.send_json(
            {"type": "players_update", "players": current_players}
        )

        # Keep connection alive
        while True:
            # Wait for any message (we don't expect client messages for now)
            await websocket.receive_text()
    except Exception:
        # Remove connection on disconnect
        if game_id in game_connections:
            game_connections[game_id].discard(websocket)
            if not game_connections[game_id]:
                del game_connections[game_id]


async def broadcast_player_list(game_id: str):
    """Broadcast the current player list to all connected clients for a game."""
    if game_id not in game_connections:
        return

    current_players = list(game_players.get(game_id, set()))
    message = {"type": "players_update", "players": current_players}

    # Send to all connected clients
    disconnected = set()
    for connection in game_connections[game_id]:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.add(connection)

    # Remove disconnected clients
    game_connections[game_id] -= disconnected
    if not game_connections[game_id]:
        del game_connections[game_id]
