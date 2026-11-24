# `elip-mcp`

A local **Model Context Protocol (MCP)** server built with **FastMCP**, **SQLite**, **NumPy**, **Google GenAI embeddings**, and **`pytest`**[cite: 9, 11, 12]. It gives MCP-compatible AI assistants persistent candidate memory, SQL-level hard dealbreaker filtering, semantic internship matching, skill-gap reporting, and a resume-audit prompt template[cite: 11, 12].

## What It Does
Instead of repeating preferences and constraints in chat prompts every session, `elip-mcp` stores a candidate profile and enforces rules predictably:
- **Persistent Candidate Memory (`memory.py` + `elip_mcp.db`):** Stores `skills`, `target_roles`, `min_stipend`, `require_remote`, and `dealbreakers` in SQLite (`candidate_profile`) alongside internship listings (`jobs`)[cite: 11, 12].
- **Hard Dealbreaker Filtering + Semantic Ranking (`server.py`):** Filters jobs in SQLite by stipend and remote mode (`work_mode`), computes semantic similarity using `gemini-embedding-001` and `NumPy` cosine similarity, and returns `semantic_score`, `why_it_fits`, and `skill_gaps`[cite: 11, 12].
- **MCP Primitives (`server.py`):**
  - **Resource (`career://profile/current`):** Reads the current candidate profile and constraints[cite: 12].
  - **Tool (`update_career_memory`):** Updates and persists candidate preferences and dealbreakers[cite: 12].
  - **Tool (`match_internships`):** Filters and ranks matching internships for a search query[cite: 12].
  - **Prompt (`audit_resume_for_job`):** Guides an MCP client to inspect the current profile and a target `job_id`, then produce fit notes, skill gaps, and 3 tailored resume bullets[cite: 12].

> **Scope Note:** Currently runs against seeded local sample internship records in `elip_mcp.db` rather than live scraped job boards[cite: 11].

## Project Structure
- `memory.py` — SQLite connection/schema setup (`get_conn`, `init_db`), Gemini embedding helper (`embed_text`), and `cosine_similarity`[cite: 11].
- `seed_jobs.py` — Seeds sample internship listings into `elip_mcp.db`[cite: 2, 8].
- `server.py` — FastMCP server (`Elip Career MCP Server`) exposing resource, tools, and prompt[cite: 12].
- `test_evals.py` — Automated `pytest` evaluation suite for dealbreakers, output fields, and edge cases[cite: 3, 9].

## Setup & Commands
Run commands from `C:\Users\Gokul\Documents\Goku\elip-mcp` using your virtual environment[cite: 1, 2]:

### 1. Configure `.env`
Add your Gemini API key to a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### 2. Seed Jobs, Inspect Server, and Run Evals
```powershell
C:\Users\Gokul\venv\Scripts\python.exe seed_jobs.py
C:\Users\Gokul\venv\Scripts\fastmcp.exe inspect server.py
C:\Users\Gokul\venv\Scripts\pytest.exe -v test_evals.py
```

### 3. Connect to an MCP Client (`stdio`)
- **Command:** `C:\Users\Gokul\venv\Scripts\python.exe`[cite: 5]
- **Args:** `["C:\\Users\\Gokul\\Documents\\Goku\\elip-mcp\\server.py"]`[cite: 6]