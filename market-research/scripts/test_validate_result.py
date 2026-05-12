"""Tests for validate-result.py — verifies the result.json schema validator."""
import json
import tempfile
from pathlib import Path

import validate_result


def _good_payload() -> dict:
    """Minimum-viable valid payload."""
    return {
        "stage": "market_research",
        "status": "ok",
        "signals": ["branch_c_title_only"],
        "started_at": "2026-05-11T14:30:00Z",
        "completed_at": "2026-05-11T14:33:12Z",
        "artifacts": [
            {"path": "market-landscape.md", "kind": "markdown"},
            {"path": "research-brief.md", "kind": "markdown"},
        ],
        "decisions": [
            {
                "type": "branch",
                "chose": "Branch C (title-only)",
                "why": "input was a title string, no PRD URL provided",
            }
        ],
        "confidence": 0.75,
        "notion_page_url": "https://www.notion.so/abc123",
        "branch": "C",
    }


def test_minimum_valid_payload_passes():
    assert validate_result.validate(_good_payload()) == []


def test_missing_required_field_fails():
    payload = _good_payload()
    del payload["stage"]
    errors = validate_result.validate(payload)
    assert any("stage" in e for e in errors)


def test_wrong_stage_const_fails():
    payload = _good_payload()
    payload["stage"] = "research"
    errors = validate_result.validate(payload)
    assert any("stage" in e or "market_research" in e for e in errors)


def test_invalid_status_enum_fails():
    payload = _good_payload()
    payload["status"] = "fine"
    errors = validate_result.validate(payload)
    assert any("status" in e for e in errors)


def test_signal_not_snake_case_fails():
    payload = _good_payload()
    payload["signals"] = ["Branch C Title Only"]
    errors = validate_result.validate(payload)
    assert any("signal" in e.lower() for e in errors)


def test_confidence_above_1_fails():
    payload = _good_payload()
    payload["confidence"] = 1.5
    errors = validate_result.validate(payload)
    assert any("confidence" in e for e in errors)


def test_confidence_below_0_fails():
    payload = _good_payload()
    payload["confidence"] = -0.1
    errors = validate_result.validate(payload)
    assert any("confidence" in e for e in errors)


def test_branch_invalid_enum_fails():
    payload = _good_payload()
    payload["branch"] = "D"
    errors = validate_result.validate(payload)
    assert any("branch" in e for e in errors)


def test_nullable_notion_page_url_accepts_null():
    payload = _good_payload()
    payload["notion_page_url"] = None
    assert validate_result.validate(payload) == []


def test_decision_missing_why_fails():
    payload = _good_payload()
    payload["decisions"] = [{"type": "branch", "chose": "X"}]  # missing why
    errors = validate_result.validate(payload)
    assert any("why" in e or "decision" in e.lower() for e in errors)


def test_decision_alternatives_optional():
    payload = _good_payload()
    payload["decisions"][0]["alternatives_considered"] = ["alt1", "alt2"]
    assert validate_result.validate(payload) == []


def test_artifact_kind_invalid_fails():
    payload = _good_payload()
    payload["artifacts"] = [{"path": "x.pdf", "kind": "pdf"}]
    errors = validate_result.validate(payload)
    assert any("kind" in e for e in errors)


def test_validate_file_writes_to_disk(tmp_path):
    """The validator's CLI accepts a file path."""
    payload_file = tmp_path / "result.json"
    payload_file.write_text(json.dumps(_good_payload()))
    errors = validate_result.validate_file(payload_file)
    assert errors == []


def test_started_after_completed_is_not_caught(tmp_path):
    """Note: temporal ordering is NOT validated by schema; that's a runtime concern."""
    payload = _good_payload()
    payload["started_at"] = "2026-05-11T15:00:00Z"
    payload["completed_at"] = "2026-05-11T14:00:00Z"
    # Schema only checks date-time format, not ordering. This should still pass.
    assert validate_result.validate(payload) == []
