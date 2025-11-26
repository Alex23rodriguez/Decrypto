from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/items/{id}")
async def read_item(_: Request, id: str):
    return {"item": id}


@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_lobby(request: Request, game_id: str):
    return templates.TemplateResponse(
        "game_lobby.html", {"request": request, "game_id": game_id}
    )
