"""Tests for refresh-modules.py — verifies the JSON snapshot writer."""
import json
import tempfile
from pathlib import Path

import refresh_modules


def test_normalize_module_entry_extracts_required_fields():
    raw = {
        "Module": "Loyalty Engine",
        "Category": ["Loyalty/CRM"],
        "State": ["Core"],
        "Features": "Earn/burn, tiers, rewards catalog",
        "Example Partners": "Punchh, Paytronix, Thanx",
    }
    normalized = refresh_modules.normalize_module(raw)
    assert normalized["module"] == "Loyalty Engine"
    assert normalized["category"] == ["Loyalty/CRM"]
    assert normalized["state"] == ["Core"]
    assert "Punchh" in normalized["example_partners"]


def test_normalize_skips_empty_titles():
    raw = {"Module": "", "Category": [], "State": [], "Features": "", "Example Partners": ""}
    assert refresh_modules.normalize_module(raw) is None


def test_write_snapshot_emits_well_formed_json():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "modules.json"
        refresh_modules.write_snapshot(
            [{"module": "X", "category": ["Ordering"], "state": ["Core"], "features": "", "example_partners": ""}],
            out,
            source_url="https://example.com",
        )
        data = json.loads(out.read_text())
        assert data["modules"][0]["module"] == "X"
        assert data["source_url"] == "https://example.com"
        assert "last_refreshed" in data
