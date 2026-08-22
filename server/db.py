import json
import sqlite3
from pathlib import Path

from config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS chunks (
                doc_id INTEGER NOT NULL,
                idx INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                FOREIGN KEY(doc_id) REFERENCES docs(id)
            );
            """
        )


def add_doc(name: str, chunks: list[str], embeddings: list[list[float]]):
    with _connect() as conn:
        cur = conn.execute("INSERT INTO docs(name) VALUES(?)", (name,))
        doc_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO chunks(doc_id, idx, text, embedding) VALUES(?,?,?,?)",
            [(doc_id, i, t, json.dumps(e)) for i, (t, e) in enumerate(zip(chunks, embeddings))],
        )
    return get_doc(doc_id)


def get_doc(doc_id: int):
    with _connect() as conn:
        row = conn.execute("SELECT id, name, created_at FROM docs WHERE id=?", (doc_id,)).fetchone()
        if not row:
            return None
        cnt = conn.execute("SELECT COUNT(*) FROM chunks WHERE doc_id=?", (doc_id,)).fetchone()[0]
        return {"id": row["id"], "name": row["name"], "created_at": row["created_at"], "chunk_count": cnt}


def list_docs() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT id, name, created_at FROM docs ORDER BY id DESC").fetchall()
        docs = []
        for r in rows:
            cnt = conn.execute("SELECT COUNT(*) FROM chunks WHERE doc_id=?", (r["id"],)).fetchone()[0]
            docs.append({"id": r["id"], "name": r["name"], "created_at": r["created_at"], "chunk_count": cnt})
        return docs


def delete_doc(doc_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM chunks WHERE doc_id=?", (doc_id,))
        conn.execute("DELETE FROM docs WHERE id=?", (doc_id,))


def load_chunks() -> list[tuple[int, str, list[float]]]:
    with _connect() as conn:
        rows = conn.execute("SELECT doc_id, text, embedding FROM chunks").fetchall()
        return [(r["doc_id"], r["text"], json.loads(r["embedding"])) for r in rows]
