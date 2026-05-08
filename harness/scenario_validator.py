"""
Scenario validator.

Checks every *.md in browser-tests/scenarios/ against the scenario contract:
  - YAML frontmatter has all required fields
  - `name` field matches filename
  - All required markdown sections (## headings) are present
  - At least one observation section is present

Run standalone:
    python3 harness/scenario_validator.py

Import in static.py:
    from scenario_validator import validate_all
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).parent.parent
SCENARIOS_DIR = ROOT / "browser-tests" / "scenarios"

REQUIRED_FRONTMATTER = {"name", "tags", "surfaces", "fixtures", "actions", "waits"}

REQUIRED_SECTIONS = {
    "Purpose",
    "User Flow",
    "Fixtures",
    "Actions",
    "Wait/Settling",
    "Asserts",
    "Report",
    "Cleanup",
}

OBSERVATION_SECTIONS = {
    "UI Observations",
    "Network Observations",
    "Server-Side Observations",
    "State Observations",
}


class ValidationError(NamedTuple):
    path: Path
    message: str


def _frontmatter_keys(text: str) -> set[str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return set()
    return {m.group(1) for m in re.finditer(r"^(\w+)\s*:", match.group(1), re.MULTILINE)}


def _sections(text: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)}


def validate_scenario(path: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    text = path.read_text()

    keys = _frontmatter_keys(text)
    if not keys:
        return [ValidationError(path, "missing frontmatter (--- block)")]

    missing_fields = REQUIRED_FRONTMATTER - keys
    if missing_fields:
        errors.append(ValidationError(path, f"missing frontmatter fields: {sorted(missing_fields)}"))

    name_match = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
    if name_match and name_match.group(1) != path.stem:
        errors.append(ValidationError(path, f"name '{name_match.group(1)}' does not match filename '{path.stem}'"))

    sections = _sections(text)
    missing_sections = REQUIRED_SECTIONS - sections
    if missing_sections:
        errors.append(ValidationError(path, f"missing sections: {sorted(missing_sections)}"))

    if not (OBSERVATION_SECTIONS & sections):
        errors.append(ValidationError(path, f"needs at least one of: {sorted(OBSERVATION_SECTIONS)}"))

    return errors


def validate_all(scenarios_dir: Path = SCENARIOS_DIR) -> list[ValidationError]:
    if not scenarios_dir.exists():
        return []
    errors: list[ValidationError] = []
    for path in sorted(scenarios_dir.glob("*.md")):
        errors.extend(validate_scenario(path))
    return errors


if __name__ == "__main__":
    errors = validate_all()
    if not errors:
        count = len(list(SCENARIOS_DIR.glob("*.md")))
        print(f"OK  {count} scenario(s) valid")
        sys.exit(0)
    for err in errors:
        print(f"FAIL  {err.path.name}: {err.message}")
    sys.exit(1)
