import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "questions.json")


def load_questions():
    with open(_PATH) as f:
        return json.load(f)


# Seniority must be compared by rank, not alphabetically ("lead" < "senior" as strings)
SENIORITY_RANK = {"junior": 0, "mid": 1, "senior": 2, "lead": 3}


def questions_for(job_role: str, seniority: str):
    """Common questions for everyone + questions for this job role, filtered by seniority."""
    rank = SENIORITY_RANK.get(seniority, 0)
    result = []
    for q in load_questions():
        if q["roles"] != ["all"] and job_role not in q["roles"]:
            continue
        if rank < SENIORITY_RANK[q.get("min_seniority", "junior")]:
            continue
        result.append(q)
    return result
