from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..auth import current_membership
from ..services.questions import questions_for
from ..services.scoring import score_open_answer

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])


class AnswerIn(BaseModel):
    question_id: str = Field(max_length=40)
    answer: str = Field(max_length=2000)


class SubmitIn(BaseModel):
    answers: list[AnswerIn]


def employee_membership(m: models.Membership = Depends(current_membership)) -> models.Membership:
    # Admins have no department and the UI never offers them the diagnostic; their answers
    # would land in "No department" and make respondents exceed headcount
    if m.role != "employee":
        raise HTTPException(403, "The diagnostic is for employees")
    return m


@router.get("/questions")
def get_questions(m: models.Membership = Depends(employee_membership)):
    qs = questions_for(m.job_role, m.seniority)
    # don't leak scoring points to the client
    return [
        {k: v for k, v in q.items() if k != "points"} | (
            {"options": [o["text"] for o in q["options"]]} if q["type"] == "mcq" else {}
        )
        for q in qs
    ]


@router.post("/submit")
def submit(body: SubmitIn, m: models.Membership = Depends(employee_membership), db: Session = Depends(get_db)):
    # Only the questions this person was actually shown are valid, and all must be answered
    bank = {q["id"]: q for q in questions_for(m.job_role, m.seniority)}
    ids = [a.question_id for a in body.answers]
    if len(ids) != len(set(ids)):
        raise HTTPException(400, "Each question can only be answered once")
    for qid in ids:
        if qid not in bank:
            raise HTTPException(400, f"Unknown question {qid}")
    missing = set(bank) - set(ids)
    if missing:
        raise HTTPException(400, f"Please answer all questions (missing: {', '.join(sorted(missing))})")
    if any(not a.answer.strip() for a in body.answers):
        raise HTTPException(400, "Answers cannot be empty")

    # Retaking replaces the previous answers instead of piling up duplicates
    db.query(models.Response).filter_by(membership_id=m.id).delete()
    for a in body.answers:
        q = bank[a.question_id]
        resp = models.Response(membership_id=m.id, question_id=q["id"], answer=a.answer.strip())
        if q["type"] == "mcq":
            option = next((o for o in q["options"] if o["text"] == a.answer), None)
            if option is None:
                raise HTTPException(400, f"Invalid option for {q['id']}")
            resp.score = option["points"]
        else:
            result = score_open_answer(q["text"], a.answer)
            resp.score = result["score"]
            resp.reason = result["reason"]
            resp.flags = result["flags"]
        db.add(resp)
    db.commit()
    return {"saved": len(body.answers)}
