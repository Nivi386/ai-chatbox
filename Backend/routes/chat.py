# routes/chat.py
# All chat-related endpoints live here, separate from main.py.

from fastapi import APIRouter, HTTPException
from database import get_connection
from models.chat_models import SessionCreate, MessageCreate
from models.chat_models import ChatRequest
from services.ai_service import ask_ai

router = APIRouter()

@router.get("/sessions")
def get_sessions():
    """Fetch all chat sessions, most recently created first."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, created_at FROM chat_sessions ORDER BY created_at DESC")
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sessions


@router.post("/sessions", status_code=201)
def create_session(session: SessionCreate):
    """Create a new, empty chat session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (title) VALUES (%s)",
        (session.title,)
    )
    conn.commit()  # writes the change permanently to the database
    new_id = cursor.lastrowid  # the auto-generated id of the row we just inserted
    cursor.close()
    conn.close()
    return {"id": new_id, "title": session.title}


@router.post("/sessions/{session_id}/messages", status_code=201)
def add_message(session_id: int, message: MessageCreate):
    """Add a new message to an existing session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
        (session_id, message.role, message.content)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {
        "id": new_id,
        "session_id": session_id,
        "role": message.role,
        "content": message.content
    }


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: int):
    """Fetch all messages belonging to a specific session, oldest first."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # First, confirm the session actually exists before looking for its messages
    cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (session_id,))
    session = cursor.fetchone()
    if session is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    cursor.execute(
        "SELECT id, role, content, created_at FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
        (session_id,)
    )
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return messages


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int):
    """Delete a session, and (thanks to our ON DELETE CASCADE) all its messages too."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (session_id,))
    session = cursor.fetchone()
    if session is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    cursor.execute("DELETE FROM chat_sessions WHERE id = %s", (session_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return None
    
@router.post("/chat")
def chat(request: ChatRequest):
    """
    Handles one turn of conversation:
    1. Creates a session if none was given.
    2. Saves the user's message.
    3. Sends the full conversation history to the AI.
    4. Saves the AI's reply.
    5. Returns the reply and the session_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    session_id = request.session_id

    if session_id is None:
        # No session yet — start a new one, using the first message as a title preview
        title_preview = request.message[:50]  # keep titles short
        cursor.execute("INSERT INTO chat_sessions (title) VALUES (%s)", (title_preview,))
        conn.commit()
        session_id = cursor.lastrowid
    else:
        # Confirm the given session actually exists
        cursor.execute("SELECT id FROM chat_sessions WHERE id = %s", (session_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Save the user's new message
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
        (session_id, "user", request.message)
    )
    conn.commit()

    # Pull the FULL conversation so far, in order — this becomes the AI's "memory"
    cursor.execute(
        "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
        (session_id,)
    )
    history = cursor.fetchall()  # already shaped as [{"role": ..., "content": ...}, ...]

    # Ask the AI, giving it the entire transcript
    reply = ask_ai(history)

    # Save the AI's reply too, so it's part of history for the *next* turn
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
        (session_id, "assistant", reply)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return {"session_id": session_id, "reply": reply}