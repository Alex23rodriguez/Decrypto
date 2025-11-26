from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for game players (game_id -> set of player names)
game_players = {}


@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, game_id: str):
    # Get current players in the game
    current_players = list(game_players.get(game_id, set()))

    return templates.TemplateResponse(
        "game_lobby.html",
        {"request": request, "game_id": game_id, "current_players": current_players},
    )


@app.post("/game/{game_id}/join", response_class=HTMLResponse)
async def join_game(request: Request, game_id: str, player_name: str = Form(...)):
    # Add player to the game
    if game_id not in game_players:
        game_players[game_id] = set()
    game_players[game_id].add(player_name)

    # Get other players (excluding current player)
    other_players = game_players[game_id] - {player_name}

    return templates.TemplateResponse(
        "game_joined.html",
        {
            "request": request,
            "game_id": game_id,
            "player_name": player_name,
            "other_players": list(other_players),
        },
    )


@app.post("/game/{game_id}/leave", response_class=HTMLResponse)
async def leave_game(request: Request, game_id: str, player_name: str = Form(...)):
    # Remove player from the game
    if game_id in game_players:
        game_players[game_id].discard(player_name)

    # Return the input form
    return templates.TemplateResponse(
        "game_leave.html",
        {"request": request, "game_id": game_id},
    )
