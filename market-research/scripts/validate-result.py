"""Validate /market-research result.json against the result-schema.json contract.

Pure-stdlib validator (no jsonschema dependency required). Enforces:
- Required top-level fields and their types
- Enum constraints on status, branch, artifact kind
- snake_case pattern on signals and decision types
- Numeric range on confidence (0..1)
- Nullability on notion_page_url
- additionalProperties: false on the top-level object and on artifact/decision items
- Required fields within each artifact and decision entry

Usage:
  python validate-result.py <path-to-result.json>

Exit 0 = valid. Exit 1 = invalid (errors printed to stderr). Exit 2 = bad CLI args.
"""
import json
import re
import sys
from pathlib import Path
from typing import List

VALID_STATUS = {"ok", "warn", "error"}
VALID_BRANCH = {"A", "B", "C"}
VALID_ARTIFACT_KIND = {"markdown", "json", "image", "screenshot", "other"}

REQUIRED_TOP = [
    "stage", "status", "signals", "started_at", "completed_at",
    "artifacts", "decisions", "confidence", "branch",
]
ALLOWED_TOP = set(REQUIRED_TOP) | {"notion_page_url"}

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
ISO_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})$"
)


def validate(payload: dict) -> List[str]:
    """Return list of validation error messages. Empty list = valid."""
    errors: List[str] = []

    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    # Required fields
    for key in REQUIRED_TOP:
        if key not in payload:
            errors.append(f"missing required field: {key}")

    # Additional properties check
    extras = set(payload.keys()) - ALLOWED_TOP
    for extra in sorted(extras):
        errors.append(f"unexpected top-level field: {extra}")

    # stage
    if "stage" in payload and payload["stage"] != "market_research":
        errors.append(f"stage must be 'market_research', got {payload['stage']!r}")

    # status
    if "status" in payload and payload["status"] not in VALID_STATUS:
        errors.append(f"status must be one of {sorted(VALID_STATUS)}, got {payload['status']!r}")

    # branch
    if "branch" in payload and payload["branch"] not in VALID_BRANCH:
        errors.append(f"branch must be one of {sorted(VALID_BRANCH)}, got {payload['branch']!r}")

    # confidence
    if "confidence" in payload:
        c = payload["confidence"]
        if not isinstance(c, (int, float)) or isinstance(c, bool):
            errors.append(f"confidence must be a number, got {type(c).__name__}")
        elif not (0 <= c <= 1):
            errors.append(f"confidence must be between 0 and 1, got {c}")

    # started_at / completed_at
    for key in ("started_at", "completed_at"):
        if key in payload:
            val = payload[key]
            if not isinstance(val, str) or not ISO_DATETIME.match(val):
                errors.append(f"{key} must be ISO 8601 datetime, got {val!r}")

    # notion_page_url
    if "notion_page_url" in payload:
        val = payload["notion_page_url"]
        if val is not None and (not isinstance(val, str) or len(val) == 0):
            errors.append(f"notion_page_url must be a non-empty string or null, got {val!r}")

    # signals
    if "signals" in payload:
        sigs = payload["signals"]
        if not isinstance(sigs, list):
            errors.append("signals must be an array")
        else:
            for i, s in enumerate(sigs):
                if not isinstance(s, str) or not SNAKE_CASE.match(s):
                    errors.append(f"signal[{i}] must be snake_case string, got {s!r}")

    # artifacts
    if "artifacts" in payload:
        arts = payload["artifacts"]
        if not isinstance(arts, list):
            errors.append("artifacts must be an array")
        else:
            for i, a in enumerate(arts):
                if not isinstance(a, dict):
                    errors.append(f"artifact[{i}] must be an object")
                    continue
                if "path" not in a:
                    errors.append(f"artifact[{i}] missing required field: path")
                elif not isinstance(a["path"], str) or len(a["path"]) == 0:
                    errors.append(f"artifact[{i}].path must be non-empty string")
                if "kind" not in a:
                    errors.append(f"artifact[{i}] missing required field: kind")
                elif a["kind"] not in VALID_ARTIFACT_KIND:
                    errors.append(
                        f"artifact[{i}].kind must be one of {sorted(VALID_ARTIFACT_KIND)}, got {a['kind']!r}"
                    )
                extra_keys = set(a.keys()) - {"path", "kind"}
                for ek in sorted(extra_keys):
                    errors.append(f"artifact[{i}] unexpected field: {ek}")

    # decisions
    if "decisions" in payload:
        decs = payload["decisions"]
        if not isinstance(decs, list):
            errors.append("decisions must be an array")
        else:
            for i, d in enumerate(decs):
                if not isinstance(d, dict):
                    errors.append(f"decision[{i}] must be an object")
                    continue
                for req in ("type", "chose", "why"):
                    if req not in d:
                        errors.append(f"decision[{i}] missing required field: {req}")
                if "type" in d and (not isinstance(d["type"], str) or not SNAKE_CASE.match(d["type"])):
                    errors.append(f"decision[{i}].type must be snake_case string, got {d.get('type')!r}")
                for str_field in ("chose", "why"):
                    if str_field in d and (not isinstance(d[str_field], str) or len(d[str_field]) == 0):
                        errors.append(f"decision[{i}].{str_field} must be non-empty string")
                if "alternatives_considered" in d:
                    alts = d["alternatives_considered"]
                    if not isinstance(alts, list) or not all(isinstance(x, str) for x in alts):
                        errors.append(f"decision[{i}].alternatives_considered must be array of strings")
                extra_keys = set(d.keys()) - {"type", "chose", "why", "alternatives_considered"}
                for ek in sorted(extra_keys):
                    errors.append(f"decision[{i}] unexpected field: {ek}")

    return errors


def validate_file(path: Path) -> List[str]:
    """Load JSON from `path` and validate. Returns error list."""
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    return validate(payload)


def main():
    if len(sys.argv) != 2:
        print("usage: validate-result.py <path-to-result.json>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        sys.exit(2)

    errors = validate_file(path)

    if errors:
        print(f"result.json invalid ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print(f"result.json valid: {path}")


if __name__ == "__main__":
    main()
