import json
from pathlib import Path
from app.core import benchmark_summary

def test_session_fixture_produces_recovery_signal():
    data=json.loads((Path(__file__).parents[1]/"fixtures/session-example.json").read_text())
    summary=benchmark_summary(data["attempts"])
    assert summary["completed"] == 2
    assert summary["recovery_rate"] > 0
