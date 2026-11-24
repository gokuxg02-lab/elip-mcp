import sqlite3
import json
import os
import numpy as np
from google import genai
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "elip_mcp.db")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_profile (
            id TEXT PRIMARY KEY,
            name TEXT DEFAULT 'Candidate',
            skills TEXT DEFAULT '[]',
            target_roles TEXT DEFAULT '[]',
            min_stipend INTEGER DEFAULT 0,
            require_remote INTEGER DEFAULT 0,
            dealbreakers TEXT DEFAULT '[]'
        )
    """)
    cur.execute("INSERT OR IGNORE INTO candidate_profile (id) VALUES ('default')")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            work_mode TEXT NOT NULL,
            stipend INTEGER NOT NULL,
            required_skills TEXT NOT NULL,
            description TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def embed_text(text: str) -> list[float]:
    res = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return res.embeddings[0].values

def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a, dtype=np.float32), np.array(b, dtype=np.float32)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / denom) if denom != 0 else 0.0