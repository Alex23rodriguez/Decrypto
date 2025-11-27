from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.routers import lobby

app = FastAPI()

# app.include_router(lobby.router)
app.include_router(lobby.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return "Welcome!"
