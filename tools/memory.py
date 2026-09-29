import sqlite3
from datetime import datetime, timezone
import config


def _connect():
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    return conn


def remember(content: str) -> str:
    """Store a fact in long-term memory."""
    conn = _connect()
    conn.execute(
        "INSERT INTO memories (content, created_at) VALUES (?, ?)",
        (content, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return f"Remembered: {content}"


def recall(query: str, limit: int = 5) -> str:
    """Basic keyword search across stored memories."""
    conn = _connect()
    cur = conn.cursor()

    keywords = [w.strip("?.,!").lower() for w in query.split() if len(w) > 2]
    if not keywords:
        cur.execute("SELECT content, created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,))
    else:
        like_clauses = " OR ".join(["LOWER(content) LIKE ?"] * len(keywords))
        params = [f"%{k}%" for k in keywords]
        cur.execute(
            f"SELECT content, created_at FROM memories WHERE {like_clauses} ORDER BY id DESC LIMIT ?",
            (*params, limit),
        )

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No relevant memories found."

    return "\n".join(f"- {content} (saved {created_at[:10]})" for content, created_at in rows)