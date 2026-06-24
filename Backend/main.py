# main.py

from fastapi import FastAPI
from routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def read_root():
    return {"message": "Hello! Your AI Chatbox backend is alive."}