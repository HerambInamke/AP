from app.auth import hash_password, verify_password
from tests.conftest import login, full_answers

NW = "Northwind Logistics"


def dashboard(client, email="asha@northwind.test", org=NW):
    headers, _ = login(client, email, org)
    return client.get("/dashboard", headers=headers)


def test_login_lists_organizations(client):
    _, data = login(client, "ravi@consult.test")
    names = {o["org_name"] for o in data["organizations"]}
    assert names == {"Northwind Logistics", "Bluepeak Retail"}


def test_wrong_password_rejected(client):
    r = client.post("/auth/login", json={"email": "asha@northwind.test", "password": "nope"})
    assert r.status_code == 401


def test_passwords_are_salted():
    a, b = hash_password("pulse123"), hash_password("pulse123")
    assert a != b and verify_password("pulse123", a) and not verify_password("x", a)


def test_employee_sees_questions(client):
    headers, _ = login(client, "priya@northwind.test", NW)
    r = client.get("/diagnostic/questions", headers=headers)
    assert r.status_code == 200
    assert any(q["id"] == "sup-drafts" for q in r.json())
    assert all("points" not in q for q in r.json())


# --- Data isolation -------------------------------------------------------

def test_cannot_select_org_you_dont_belong_to(client):
    headers, data = login(client, "asha@northwind.test")
    own = {o["org_id"] for o in data["organizations"]}
    other = next(i for i in (1, 2) if i not in own)
    r = client.post("/auth/select-org", json={"org_id": other}, headers=headers)
    assert r.status_code == 403


def test_admin_cannot_see_other_org(client):
    # Old bug: ?org_id= let any admin read any org. The org now comes from the token only.
    headers, _ = login(client, "asha@northwind.test", NW)
    r = client.get("/dashboard?org_id=2", headers=headers)
    assert r.status_code == 200
    assert r.json()["organization"] == NW


def test_multi_org_user_sees_only_selected_org(client):
    r = dashboard(client, "ravi@consult.test", "Bluepeak Retail")
    assert r.json()["organization"] == "Bluepeak Retail"
    # Ravi is only an employee at Northwind
    assert dashboard(client, "ravi@consult.test", NW).status_code == 403


def test_employee_cannot_see_dashboard(client):
    assert dashboard(client, "priya@northwind.test").status_code == 403


def test_token_without_org_is_rejected(client):
    headers, _ = login(client, "priya@northwind.test")
    assert client.get("/reports/me", headers=headers).status_code == 400


# --- Client request 1: no small groups -----------------------------------

def test_small_departments_are_pooled_and_hidden(client):
    d = dashboard(client).json()
    assert [x["department"] for x in d["departments"]] == ["Support"]  # only group with 5 respondents
    assert d["departments"][0]["respondents"] == 5
    other = d["other_teams"]
    assert other["hidden"] is True
    assert set(other["includes"]) == {"Engineering", "HR", "Sales"}
    assert "average_score" not in other  # no numbers leak for <5 people


def test_risks_only_come_from_visible_groups(client):
    risks = {r["risk"]: r["people"] for r in dashboard(client).json()["top_risks"]}
    # Support: Priya + Joseph shared customer data, Kavitha unreviewed output.
    # Sales/Engineering flags must not appear while they are hidden.
    assert risks == {"customer_data_shared": 2, "unreviewed_output": 1}


def test_overall_uses_visible_people_only(client):
    d = dashboard(client).json()
    # Otherwise overall minus Support would reveal the hidden pool's average
    assert d["overall"]["respondents"] == 5
    assert d["overall"]["average_score"] == d["departments"][0]["average_score"]


def test_pool_becomes_visible_at_five(client):
    for email in ["neha@northwind.test", "dev@northwind.test"]:
        h, _ = login(client, email, NW)
        r = client.post("/diagnostic/submit", headers=h, json={"answers": full_answers(client, h)})
        assert r.status_code == 200
    other = dashboard(client).json()["other_teams"]
    assert other["hidden"] is False and other["respondents"] == 5


def test_department_average_is_per_person(client):
    support = dashboard(client).json()["departments"][0]
    # person averages: priya 2.5, arjun 5, kavitha 3, farah 4, joseph 2 -> 3.3
    assert support["average_score"] == 3.3
    assert support["level"] == "Practitioner"


# --- Client request 2: right to delete -----------------------------------

def test_employee_can_delete_their_data(client):
    h, _ = login(client, "priya@northwind.test", NW)
    assert client.delete("/reports/me", headers=h).json()["deleted"] == 2
    assert client.get("/reports/me", headers=h).json()["answered"] == 0
    # Support drops to 4 respondents -> disappears from the dashboard immediately
    d = dashboard(client).json()
    assert d["departments"] == []
    assert "Support" in d["other_teams"]["includes"]


def test_delete_only_affects_selected_org(client):
    h, _ = login(client, "ravi@consult.test", NW)
    client.post("/diagnostic/submit", headers=h, json={"answers": full_answers(client, h)})
    h2, _ = login(client, "ravi@consult.test", "Bluepeak Retail")
    client.delete("/reports/me", headers=h2)
    assert client.get("/reports/me", headers=h).json()["answered"] > 0


# --- Diagnostic submission -----------------------------------------------

def test_submit_and_retake_replaces_answers(client):
    h, _ = login(client, "dev@northwind.test", NW)
    answers = full_answers(client, h)
    for _ in range(2):
        assert client.post("/diagnostic/submit", headers=h, json={"answers": answers}).status_code == 200
    assert client.get("/reports/me", headers=h).json()["answered"] == len(answers)


def test_submit_rejects_incomplete_foreign_and_duplicate(client):
    h, _ = login(client, "dev@northwind.test", NW)
    answers = full_answers(client, h)

    def post(a):
        return client.post("/diagnostic/submit", headers=h, json={"answers": a}).status_code

    assert post(answers[:-1]) == 400                                              # missing one
    assert post(answers + [{"question_id": "sup-drafts", "answer": "x"}]) == 400  # not their question
    assert post(answers + [answers[0]]) == 400                                    # duplicate
    assert post([{**a, "answer": " "} for a in answers]) == 400                   # empty


# --- Own feature: risk -> action -----------------------------------------

def test_dashboard_risks_show_where_and_what_to_do(client):
    risks = {r["risk"]: r for r in dashboard(client).json()["top_risks"]}
    cds = risks["customer_data_shared"]
    assert cds["label"] == "Shared customer data with an AI tool"
    assert cds["teams"] == [{"team": "Support", "people": 2, "of": 5}]
    assert cds["share"] == 0.4
    assert cds["action"]  # a concrete team action, from the risk catalog


def test_risk_teams_include_visible_pool_but_never_hidden_departments(client):
    for email in ["neha@northwind.test", "dev@northwind.test"]:
        h, _ = login(client, email, NW)
        client.post("/diagnostic/submit", headers=h, json={"answers": full_answers(client, h)})
    teams = {t["team"] for r in dashboard(client).json()["top_risks"] for t in r["teams"]}
    assert teams <= {"Support", "Other teams"}  # Sales/Engineering only appear pooled


def test_report_risks_come_with_a_personal_action(client):
    h, _ = login(client, "priya@northwind.test", NW)
    risks = client.get("/reports/me", headers=h).json()["risks"]
    assert risks == [{
        "risk": "customer_data_shared",
        "label": "Shared customer data with an AI tool",
        "action": risks[0]["action"],
    }]
    assert "placeholder" in risks[0]["action"]


def test_unknown_email_still_runs_password_hash(client, monkeypatch):
    # Timing side channel: unknown emails used to return ~20x faster than real ones
    from app.routes import auth_routes
    calls = []
    real = auth_routes.verify_password
    monkeypatch.setattr(auth_routes, "verify_password", lambda p, h: calls.append(h) or real(p, h))
    r = client.post("/auth/login", json={"email": "nobody@nowhere.test", "password": "x"})
    assert r.status_code == 401 and calls == [auth_routes._DUMMY_HASH]


def test_admins_cannot_take_the_diagnostic(client):
    h, _ = login(client, "asha@northwind.test", NW)
    assert client.get("/diagnostic/questions", headers=h).status_code == 403
    assert client.post("/diagnostic/submit", headers=h, json={"answers": []}).status_code == 403
