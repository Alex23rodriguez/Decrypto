from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/game")


@router.get("/game/{game_id}", response_class=HTMLResponse)
async def game_page(request: Request, game_id: str):
    return templates.TemplateResponse(
        "index.html", {"request": request, "game_id": game_id}
    )
