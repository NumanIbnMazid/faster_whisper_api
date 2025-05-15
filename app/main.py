from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.transcribe import router as transcribe_router
from app.routers.websocket import router as websocket_router
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(title="Faster Whisper API")

# CORS for WebSocket and HTTP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://apps.nim23.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router, prefix="/api", tags=["transcribe"])
app.include_router(websocket_router, tags=["websocket"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Faster Whisper API!"}
