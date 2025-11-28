from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.storage import get_games_storage

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/game")

games = get_games_storage()


@router.get("/game/{room_id}", response_class=HTMLResponse)
async def game_page(request: Request, room_id: str):
    player_id = request.cookies.get("player_token")

    room_info = games.get_room_info(room_id, player_id)

    if "error" in room_info:
        print(request.cookies.get("player_token"))
        raise HTTPException(status_code=403, detail=room_info["error"])

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_id": room_id,
            "player_name": room_info["player_name"],
            "players": room_info["players"],
        },
    )
