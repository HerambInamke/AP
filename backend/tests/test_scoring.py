import json
from pathlib import Path

import pytest

from app.services import scoring

MOCKS = json.loads((Path(__file__).parent.parent / "data" / "mock_ai_responses.json").read_text())


@pytest.mark.parametrize("raw,score,flags", [
    (MOCKS[0], 4, []),
    (MOCKS[4], 3, ["customer_data_shared"]),
    (MOCKS[5], None, []),                    # score 7 is out of range -> not trusted
    (MOCKS[6], 3, ["unreviewed_output"]),    # missing reason -> default text
    (MOCKS[7], None, []),                    # "four" is not a number
    (MOCKS[8], 2, []),                       # made-up flags dropped
    (MOCKS[9], 4, []),                       # ```json fenced
    ("not json at all", None, []),
    ("[1, 2]", None, []),
    ('{"score": true}', None, []),
])
def test_parse_score(raw, score, flags):
    r = scoring.parse_score(raw)
    assert r["score"] == score and r["flags"] == flags and r["reason"]


def test_llm_failure_does_not_crash(monkeypatch):
    def boom(*_):
        raise TimeoutError
    monkeypatch.setattr(scoring.llm, "score_answer", boom)
    assert scoring.score_open_answer("q", "a")["score"] is None


def test_every_allowed_flag_has_label_and_actions():
    from app.services.risks import RISKS
    assert scoring.ALLOWED_FLAGS == set(RISKS)
    for r in RISKS.values():
        assert r["label"] and r["team_action"] and r["your_action"]
