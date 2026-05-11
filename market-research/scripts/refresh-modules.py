"""Refresh the Modules DB snapshot from the Notion Technical Partner Strategy page.

Usage:
  python refresh-modules.py [--data <path-to-rows.json>] [--out <path-to-modules.json>]

The --data argument expects a JSON file containing the rows fetched from Notion
(via mcp__claude_ai_Notion__notion-query-data-sources). When omitted, the script
prints instructions for fetching the rows.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Iterable, Optional

SOURCE_URL = "https://www.notion.so/8662d31182004bc5a3f2b547f9ba6dd7"
DEFAULT_OUT = Path(__file__).parent.parent / "knowledge" / "modules.json"


def normalize_module(raw: dict) -> Optional[dict]:
    """Normalize one row from the Notion query into the snapshot schema."""
    title = (raw.get("Module") or "").strip()
    if not title:
        return None
    return {
        "module": title,
        "category": list(raw.get("Category") or []),
        "state": list(raw.get("State") or []),
        "features": (raw.get("Features") or "").strip(),
        "example_partners": (raw.get("Example Partners") or "").strip(),
    }


def write_snapshot(modules: Iterable[dict], out_path: Path, *, source_url: str) -> None:
    """Serialize the snapshot atomically."""
    payload = {
        "source_url": source_url,
        "last_refreshed": dt.date.today().isoformat(),
        "modules": list(modules),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.data:
        print(
            "No --data file provided.\n"
            "To refresh, first fetch the Modules DB rows in Claude Code:\n"
            "  mcp__claude_ai_Notion__notion-query-data-sources\n"
            "    data_source_url: collection://fac5e83e-ef43-4dc4-8038-0b2fb4a76781\n"
            "Save the response rows as JSON to /tmp/modules-rows.json, then re-run\n"
            "this script with --data /tmp/modules-rows.json"
        )
        return

    raw_rows = json.loads(args.data.read_text())
    normalized = [m for m in (normalize_module(r) for r in raw_rows) if m is not None]
    write_snapshot(normalized, args.out, source_url=SOURCE_URL)
    print(f"Wrote {len(normalized)} modules to {args.out}")


if __name__ == "__main__":
    main()
