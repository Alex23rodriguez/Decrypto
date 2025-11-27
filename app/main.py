from fastapi import FastAPI

from app.routers import lobby

app = FastAPI()

# app.include_router(lobby.router)
app.include_router(lobby.router)


@app.get("/")
async def root():
    return "Welcome!"
