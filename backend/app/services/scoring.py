import json
import logging
import re

from . import llm
from .risks import RISKS

log = logging.getLogger(__name__)

ALLOWED_FLAGS = set(RISKS)
UNSCORED_REASON = "AI score unavailable; this answer was not counted in your score."


def parse_score(raw: str) -> dict:
    """Turn raw model text into a trusted result.

    Models return code fences, out-of-range scores, words instead of numbers and
    made-up flags. Anything we can't trust becomes score=None (excluded from
    averages) rather than a guess.
    """
    unscored = {"score": None, "reason": UNSCORED_REASON, "flags": []}
    match = re.search(r"\{.*\}", raw or "", re.DOTALL)  # strips ```json fences and chatter
    if not match:
        return unscored
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return unscored
    if not isinstance(data, dict):
        return unscored

    score = data.get("score")
    # bool is an int subclass; "four"/7/3.5 are all rejected, not coerced
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        return unscored

    flags = data.get("flags")
    flags = [f for f in flags if f in ALLOWED_FLAGS] if isinstance(flags, list) else []
    reason = data.get("reason")
    reason = reason.strip() if isinstance(reason, str) and reason.strip() else "No reason given by the AI."
    return {"score": score, "reason": reason, "flags": sorted(set(flags))}


def score_open_answer(question_text: str, answer: str) -> dict:
    try:
        raw = llm.score_answer(question_text, answer)
    except Exception:  # network/HTTP/provider errors must not fail the whole submission
        log.exception("LLM scoring failed")
        return {"score": None, "reason": UNSCORED_REASON, "flags": []}
    return parse_score(raw)
