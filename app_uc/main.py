import uvicorn
from pathlib import Path
import asyncio

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from apis import emissions, upload
from services.mongo_service import verify_connection, close_connection 

app = FastAPI(title="UC Backend API", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(emissions.router)
app.include_router(upload.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup_event():
    # Initialize the MongoDB connection
    await verify_connection()


@app.on_event("shutdown")
async def shutdown_event():
    await close_connection()  


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
