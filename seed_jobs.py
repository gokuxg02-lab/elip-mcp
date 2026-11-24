import json
from memory import init_db, get_conn, embed_text

JOBS = [
    {
        "title": "SDE Intern (AI Career Agent)",
        "company": "Elip (YC W25)",
        "location": "Gurugram / Bengaluru",
        "work_mode": "Remote",
        "stipend": 75000,
        "required_skills": ["Python", "LLMs", "Tool Calling", "Semantic Search", "SQL"],
        "description": "Build LLM-powered conversational agents with deterministic tool calling, persistent context memory, and semantic search."
    },
    {
        "title": "Edge AI & Computer Vision Intern",
        "company": "RoboSense Labs",
        "location": "Mumbai",
        "work_mode": "On-site",
        "stipend": 35000,
        "required_skills": ["Python", "OpenCV", "MediaPipe", "ESP32", "C++"],
        "description": "Build real-time wireless camera streaming and hand-tracking pipelines on embedded hardware."
    },
    {
        "title": "AI Infrastructure & Search Intern",
        "company": "VectorScale",
        "location": "Bengaluru",
        "work_mode": "Remote",
        "stipend": 60000,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Vector Embeddings", "Eval Suites"],
        "description": "Develop hybrid retrieval pipelines, MCP integrations, and automated LLM evaluation harnesses."
    },
    {
        "title": "Unpaid Frontend Intern",
        "company": "WebStarter",
        "location": "Pune",
        "work_mode": "On-site",
        "stipend": 0,
        "required_skills": ["HTML", "CSS", "JavaScript"],
        "description": "Build static marketing pages in-office. Unpaid 3-month internship."
    }
]

def seed():
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM jobs")
    
    for j in JOBS:
        text = f"{j['title']} at {j['company']} ({j['work_mode']}, ₹{j['stipend']}/mo): {j['description']} Skills: {', '.join(j['required_skills'])}"
        vec = embed_text(text)
        cur.execute("""
            INSERT INTO jobs (title, company, location, work_mode, stipend, required_skills, description, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            j["title"], j["company"], j["location"], j["work_mode"],
            j["stipend"], json.dumps(j["required_skills"]), j["description"], json.dumps(vec)
        ))
    
    conn.commit()
    conn.close()
    print(f"Seeded {len(JOBS)} jobs into elip_mcp.db")

if __name__ == "__main__":
    seed()