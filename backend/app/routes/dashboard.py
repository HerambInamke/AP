from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import MIN_GROUP_SIZE
from ..db import get_db
from .. import models
from ..auth import current_membership
from ..utils import maturity_level
from ..services.risks import RISKS

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

OTHER_TEAMS = "Other teams"
NO_DEPARTMENT = "No department"


def _summary(people):
    """people: list of per-person dicts. Department score = mean of each person's average."""
    avgs = [p["avg"] for p in people if p["avg"] is not None]
    avg = sum(avgs) / len(avgs) if avgs else None
    return {
        "respondents": len(people),
        "average_score": round(avg, 2) if avg is not None else None,
        "level": maturity_level(avg),
    }


@router.get("")
def org_dashboard(m: models.Membership = Depends(current_membership), db: Session = Depends(get_db)):
    if m.role != "admin":
        raise HTTPException(403, "Admins only")
    # The org always comes from the signed token, never from the request (was a cross-org leak)
    org = m.org

    headcount = defaultdict(int)
    for mem in db.query(models.Membership).filter_by(org_id=org.id, role="employee"):
        headcount[mem.department.name if mem.department else NO_DEPARTMENT] += 1

    rows = (
        db.query(models.Response, models.Membership)
        .join(models.Membership, models.Response.membership_id == models.Membership.id)
        .filter(models.Membership.org_id == org.id)
        .all()
    )
    people = {}
    for r, mem in rows:
        p = people.setdefault(mem.id, {
            "dept": mem.department.name if mem.department else NO_DEPARTMENT,
            "scores": [], "flags": set(),
        })
        if r.score is not None:
            p["scores"].append(r.score)
        p["flags"].update(r.flags or [])
    for p in people.values():
        p["avg"] = sum(p["scores"]) / len(p["scores"]) if p["scores"] else None

    by_dept = defaultdict(list)
    for p in people.values():
        by_dept[p["dept"]].append(p)

    # Client rule: groups under MIN_GROUP_SIZE respondents are never shown on their own
    all_depts = sorted({d.name for d in org.departments} | set(by_dept))
    departments, pooled, pooled_names = [], [], []
    for name in all_depts:
        group = by_dept.get(name, [])
        if len(group) >= MIN_GROUP_SIZE:
            departments.append({"department": name, "employees": headcount[name], **_summary(group)})
        else:
            pooled += group
            pooled_names.append(name)

    other = None
    if pooled_names:
        other = {"department": OTHER_TEAMS, "includes": pooled_names, "hidden": len(pooled) < MIN_GROUP_SIZE}
        if not other["hidden"]:
            other |= _summary(pooled)

    # Risks only from people whose group is visible; counted per person, not per answer
    visible_groups = [(d["department"], by_dept[d["department"]]) for d in departments]
    if other and not other["hidden"]:
        visible_groups.append((OTHER_TEAMS, pooled))
    visible = [p for _, group in visible_groups for p in group]

    # Risk -> action: for each risk, who has it, where it's concentrated, and what to do
    team_size = {team: len(group) for team, group in visible_groups}
    risk_teams = defaultdict(dict)
    for team, group in visible_groups:
        for p in group:
            for f in p["flags"]:
                risk_teams[f][team] = risk_teams[f].get(team, 0) + 1
    top_risks = []
    for flag, teams in risk_teams.items():
        affected = sum(teams.values())
        top_risks.append({
            "risk": flag,
            "label": RISKS.get(flag, {}).get("label", flag),
            "people": affected,
            "share": round(affected / len(visible), 2),
            "teams": [{"team": t, "people": n, "of": team_size[t]}
                      for t, n in sorted(teams.items(), key=lambda kv: -kv[1])],
            "action": RISKS.get(flag, {}).get("team_action"),
        })
    top_risks.sort(key=lambda r: (-r["people"], r["risk"]))

    total = len(people)
    return {
        "organization": org.name,
        "min_group_size": MIN_GROUP_SIZE,
        "respondents": total,
        # Built from visible people only: an all-people average minus the visible
        # departments would reveal a hidden group's score by subtraction
        "overall": _summary(visible) if visible else None,
        "departments": departments,
        "other_teams": other,
        "top_risks": top_risks[:5],
    }
