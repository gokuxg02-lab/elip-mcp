import json
from memory import init_db, get_conn
from server import update_career_memory, match_internships


def setup_function():
    """Reset the default candidate profile before each test."""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE candidate_profile
        SET skills='[]', target_roles='[]', min_stipend=0, require_remote=0, dealbreakers='[]'
        WHERE id='default'
        """
    )
    conn.commit()
    conn.close()


def test_dealbreaker_enforcement():
    """Verify remote and stipend constraints filter out non-matching roles."""
    update_career_memory(
        name="Gokul",
        skills=["Python", "OpenCV", "SQL", "LLMs"],
        min_stipend=50000,
        require_remote=True,
        dealbreakers=["on-site", "unpaid"],
    )
    raw = match_internships(query="AI engineering and Python internships")
    data = json.loads(raw)

    matches = data.get("matches", [])
    assert len(matches) > 0, "Should return at least one valid remote match"

    for job in matches:
        assert job["work_mode"].lower() == "remote", (
            f"Dealbreaker violated! Returned non-remote job: {job}"
        )
        assert job["stipend_inr"] >= 50000, (
            f"Dealbreaker violated! Returned low-pay job: {job}"
        )


def test_match_contains_explanations_and_skill_gaps():
    """Verify returned matches include score, fit explanation, and skill gaps."""
    update_career_memory(
        name="Gokul",
        skills=["Python", "OpenCV", "SQL", "LLMs"],
        min_stipend=50000,
        require_remote=True,
        dealbreakers=["on-site", "unpaid"],
    )
    raw = match_internships(query="AI engineering and Python internships")
    data = json.loads(raw)

    matches = data.get("matches", [])
    assert len(matches) > 0

    top = matches[0]
    assert "semantic_score" in top
    assert "why_it_fits" in top
    assert "skill_gaps" in top
    assert isinstance(top["skill_gaps"], list)


def test_impossible_stipend_returns_no_matches():
    """Verify an unreachable stipend floor cleanly returns zero matches."""
    update_career_memory(
        name="Gokul",
        skills=["Python", "OpenCV", "SQL", "LLMs"],
        min_stipend=10_000_000,
        require_remote=True,
        dealbreakers=["on-site", "unpaid"],
    )
    raw = match_internships(query="AI engineering and Python internships")
    data = json.loads(raw)

    assert data.get("matches") == []