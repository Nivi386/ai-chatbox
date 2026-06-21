# services/ai_service.py

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"


def ask_ai(messages: list) -> str:
    """
    Sends a full conversation history to the AI model and returns its reply.
    'messages' must be a list of dicts like [{"role": "user", "content": "..."}, ...]
    in chronological order — this is how the model 'remembers' the conversation.
    """
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    })
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]