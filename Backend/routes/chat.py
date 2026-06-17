# routes/chat.py
# All chat-related endpoints live here, separate from main.py.

from fastapi import APIRouter, HTTPException
from database import get_connection
from models.chat_models import SessionCreate, MessageCreate

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