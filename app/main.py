from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/items/{id}")
async def read_item(_: Request, id: str):
    return {"item": id}
