from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, game_id: str):
    return templates.TemplateResponse(
        "game_lobby.html", {"request": request, "game_id": game_id}
    )


@app.post("/game/{game_id}/join", response_class=HTMLResponse)
async def join_game(request: Request, game_id: str, player_name: str = Form(...)):
    return templates.TemplateResponse(
        "game_joined.html",
        {"request": request, "game_id": game_id, "player_name": player_name},
    )
