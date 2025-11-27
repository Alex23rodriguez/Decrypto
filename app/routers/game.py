from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routers.lobby import Games

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/game")


@router.get("/game/{room_id}", response_class=HTMLResponse)
async def game_page(request: Request, room_id: str):
    user_token = request.cookies.get("user_token")
    if not user_token or user_token not in Games[room_id]:
        raise HTTPException(status_code=403, detail="Invalid session")
    print("found user token: ", user_token)
    player_data = Games[room_id][user_token]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_id": room_id,
            "player_name": player_data,
        },
    )
