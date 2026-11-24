import json
from fastmcp import FastMCP
from memory import init_db, get_conn, embed_text, cosine_similarity

init_db()
mcp = FastMCP("Elip Career MCP Server")

# --- MCP RESOURCE: Live Candidate Profile Context ---
@mcp.resource("career://profile/current")
def get_profile_resource() -> str:
    """Returns the candidate's persistent profile, skills, and hard dealbreakers."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, skills, target_roles, min_stipend, require_remote, dealbreakers FROM candidate_profile WHERE id='default'")
    row = cur.fetchone()
    conn.close()
    return json.dumps({
        "name": row[0],
        "skills": json.loads(row[1]),
        "target_roles": json.loads(row[2]),
        "min_stipend_inr": row[3],
        "require_remote": bool(row[4]),
        "dealbreakers": json.loads(row[5]),
    }, indent=2)

# --- MCP TOOL 1: Update Persistent Candidate Memory ---
@mcp.tool()
def update_career_memory(
    name: str | None = None,
    skills: list[str] | None = None,
    target_roles: list[str] | None = None,
    min_stipend: int | None = None,
    require_remote: bool | None = None,
    dealbreakers: list[str] | None = None,
) -> str:
    """Persistently saves candidate skills, target roles, and hard dealbreakers across sessions."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, skills, target_roles, min_stipend, require_remote, dealbreakers FROM candidate_profile WHERE id='default'")
    curr = cur.fetchone()

    cur.execute("""
        UPDATE candidate_profile
        SET name=?, skills=?, target_roles=?, min_stipend=?, require_remote=?, dealbreakers=?
        WHERE id='default'
    """, (
        name if name is not None else curr[0],
        json.dumps(skills) if skills is not None else curr[1],
        json.dumps(target_roles) if target_roles is not None else curr[2],
        min_stipend if min_stipend is not None else curr[3],
        int(require_remote) if require_remote is not None else curr[4],
        json.dumps(dealbreakers) if dealbreakers is not None else curr[5],
    ))
    conn.commit()
    conn.close()
    return f"Updated persistent memory:\n{get_profile_resource()}"

# --- MCP TOOL 2: Hybrid Semantic Search + Dealbreaker Enforcement ---
@mcp.tool()
def match_internships(query: str, top_k: int = 3) -> str:
    """Finds internships matching the query while strictly enforcing saved dealbreakers (remote-only, min stipend)."""
    profile = json.loads(get_profile_resource())
    conn = get_conn()
    cur = conn.cursor()

    sql = "SELECT id, title, company, location, work_mode, stipend, required_skills, description, embedding FROM jobs WHERE stipend >= ?"
    params = [profile["min_stipend_inr"]]

    if profile["require_remote"]:
        sql += " AND LOWER(work_mode) = 'remote'"

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return json.dumps({"matches": [], "note": "No roles passed your hard dealbreaker filters."})

    q_vec = embed_text(query)
    user_skills = {s.lower() for s in profile["skills"]}
    results = []

    for r in rows:
        req_skills = json.loads(r[6])
        matched_skills = [s for s in req_skills if s.lower() in user_skills]
        missing_skills = [s for s in req_skills if s.lower() not in user_skills]
        sim_score = cosine_similarity(q_vec, json.loads(r[8]))

        results.append({
            "job_id": r[0],
            "title": r[1],
            "company": r[2],
            "work_mode": r[4],
            "stipend_inr": r[5],
            "semantic_score": round(sim_score, 4),
            "why_it_fits": f"Matches skills: {matched_skills}" if matched_skills else "Strong semantic domain alignment",
            "skill_gaps": missing_skills,
            "description": r[7],
        })

    results.sort(key=lambda x: x["semantic_score"], reverse=True)
    return json.dumps({"enforced_constraints": profile, "matches": results[:top_k]}, indent=2)

# --- MCP PROMPT: Reusable Resume Audit Workflow ---
@mcp.prompt()
def audit_resume_for_job(job_id: int) -> str:
    """Generates a structured prompt instructing the MCP client to audit the user's profile against a target job."""
    return (
        f"Read the resource `career://profile/current` and run `match_internships` to inspect job_id={job_id}. "
        "Then provide: (1) a plain-English explanation of why the candidate fits, "
        "(2) honest skill gaps, and (3) 3 concrete resume bullet points tailored to this exact role."
    )

if __name__ == "__main__":
    mcp.run()