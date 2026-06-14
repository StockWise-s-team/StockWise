import json
from pathlib import Path

from app.agents.master_router import deterministic_route
from app.agents.risk_manager_agent import RiskManagerAgent


def test_safety_eval_fixture():
    fixture_path = Path(__file__).parents[2] / "evals" / "safety_cases.json"
    cases = json.loads(fixture_path.read_text(encoding="utf-8"))
    for case in cases[:5]:
        intent = deterministic_route(case["message"]).intent
        _, flags, has_disclaimer = RiskManagerAgent().sanitize("", case["message"], intent)
        for expected in case.get("expected_flags", []):
            assert expected in flags
        if case.get("expected_disclaimer"):
            assert has_disclaimer is True
