import os
import tempfile
import pytest

# Isolated throwaway DB so tests never touch (or leave behind) a real database file
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["AI_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app import seed  # noqa: E402


@pytest.fixture()
def client():
    seed.run()
    return TestClient(app)


def login(client, email, org_name=None):
    r = client.post("/auth/login", json={"email": email, "password": "pulse123"})
    data = r.json()
    token = data["token"]
    if org_name:
        org = next(o for o in data["organizations"] if o["org_name"] == org_name)
        token = client.post("/auth/select-org", json={"org_id": org["org_id"]},
                            headers={"Authorization": f"Bearer {token}"}).json()["token"]
    return {"Authorization": f"Bearer {token}"}, data


def full_answers(client, headers):
    """A valid, complete submission for whatever questions this user is shown."""
    qs = client.get("/diagnostic/questions", headers=headers).json()
    return [
        {"question_id": q["id"],
         "answer": q["options"][-1] if q["type"] == "mcq" else "I drafted emails with AI and reviewed them."}
        for q in qs
    ]
