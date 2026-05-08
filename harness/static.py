"""
Static invariant tests.
No server, no app imports, no network calls.
All checks are pure filesystem reads, text analysis, and AST parsing.
Target: < 0.3s total.

HOW TO USE THIS FILE
====================
Copy it into your project's harness/ directory, then replace or extend
the examples below with checks for your project's specific invariants.

Run:
  python3 -m pytest harness/static.py -q --tb=short
  ./harness/testing.sh static

WHAT BELONGS HERE
=================
  - File existence (required files must be present)
  - Forbidden patterns (code that should never appear)
  - Required patterns (code that must appear in specific files)
  - AST-level structure checks (import presence, constant coverage)
  - Dependency policy (pinned versions, banned packages)
  - Documentation invariants (required sections, placeholder validity)

WHAT DOES NOT BELONG HERE
==========================
  - Anything that imports your app code
  - Anything that starts a server or database
  - Anything that writes to files
  - Anything that makes a network call
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

# ── Paths — adapt these to your project ──────────────────────────────────────

SRC           = ROOT / "src"           # your source root
ENV_EXAMPLE   = ROOT / ".env.example"
REQUIREMENTS  = ROOT / "requirements.txt"   # or package.json, pyproject.toml

# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: File existence
# Use this to enforce that required files are always present.
# ─────────────────────────────────────────────────────────────────────────────

# EXAMPLE: uncomment and adapt for your project
# def test_env_example_exists():
#     """.env.example must exist and document every env var the app reads.
#
#     If this fails: new contributors cannot start the app — they have no
#     reference for which env vars are required.
#     """
#     assert ENV_EXAMPLE.exists(), \
#         ".env.example must exist — document all required environment variables here"


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Forbidden string patterns
# Use re.compile for multi-file checks that should never match anywhere.
# ─────────────────────────────────────────────────────────────────────────────

SILENT_EXCEPTION = re.compile(
    r"except\s+(Exception|BaseException)\s*:\s*\n\s*(pass|\.\.\.)"
)

def test_no_silent_exceptions():
    """Silent exception handlers must not exist in production source.

    If this fails: crashes are swallowed silently — bugs become invisible,
    production incidents have no log evidence, debugging takes hours longer.

    Fix: add logging (log.exception(...)) or re-raise.
    """
    for path in ROOT.glob("**/*.py"):
        if any(skip in str(path) for skip in ["harness/", ".venv/", "venv/"]):
            continue
        src = path.read_text()
        assert not SILENT_EXCEPTION.search(src), \
            f"Silent exception in {path} — log it or re-raise"


HARDCODED_CREDENTIAL = re.compile(
    r'(?:password|secret|api_key|token|passwd)\s*=\s*["\'][^"\']{8,}["\']',
    re.IGNORECASE,
)

def test_no_hardcoded_credentials():
    """Credential literals must not appear in source files.

    If this fails: secrets will be committed to version control and
    exposed in logs, error messages, and repository history.
    """
    for path in ROOT.glob("**/*.py"):
        if any(skip in str(path) for skip in ["harness/", ".venv/", "venv/", "test"]):
            continue
        src = path.read_text()
        assert not HARDCODED_CREDENTIAL.search(src), \
            f"Possible hardcoded credential in {path} — use environment variables"


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Required patterns
# Use this to assert that a required element appears somewhere in a file.
# ─────────────────────────────────────────────────────────────────────────────

# Example: every route module must reference an auth check
# Adapt the glob and the required string to your project.

# def test_routes_use_auth():
#     """All route files must apply the auth middleware.
#
#     If this fails: an unprotected route was added. Every endpoint
#     must verify the session/token before processing the request.
#     """
#     for path in ROOT.glob("src/routes/*.js"):
#         src = path.read_text()
#         assert "authMiddleware" in src, \
#             f"{path.name} must apply authMiddleware"


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: AST constant coverage
# Use this to ensure all items in a known set are handled somewhere.
# Classic use case: event type switch statements, command registries.
# ─────────────────────────────────────────────────────────────────────────────

def _string_constants_in_tuple(path: Path, var_name: str) -> set[str]:
    """Return string literals assigned to a top-level tuple/list variable."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == var_name for t in node.targets):
            continue
        if isinstance(node.value, (ast.Tuple, ast.List)):
            return {
                elt.value
                for elt in node.value.elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            }
    return set()


# Example: ensure every event type in KNOWN_EVENTS is handled in the dispatcher
# Adapt to your constants file and handler file.

# EVENTS_PY = SRC / "events.py"
# HANDLER_PY = SRC / "handler.py"
#
# def test_all_events_handled():
#     """Every event type in KNOWN_EVENTS must have a case in the handler.
#
#     If this fails: a new event type was added to the registry but the
#     handler has no case for it — events are dropped silently at runtime.
#     """
#     known = _string_constants_in_tuple(EVENTS_PY, "KNOWN_EVENTS")
#     handler_src = HANDLER_PY.read_text()
#     missing = {e for e in known if e not in handler_src}
#     assert not missing, f"Events not handled: {missing}"


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Documentation invariants
# Use this to check that templates, configs, and docs contain required content.
# ─────────────────────────────────────────────────────────────────────────────

def test_harness_md_exists():
    """STRATA.md must exist as the canonical testing reference.

    If this fails: contributors and AI assistants have no testing guide.
    """
    assert (ROOT / "STRATA.md").exists(), "STRATA.md must exist"


def test_tracking_dirs_exist():
    """Feature and issue tracking directories must exist.

    If this fails: the tracking workflow has no home — contributors will
    skip tracking files and changes will be made without test plans.
    """
    for d in ["features/todo", "features/done", "issues/todo", "issues/done"]:
        assert (ROOT / d).is_dir(), f"{d}/ must exist"


def test_browser_tests_structure_exists():
    """browser-tests/ directory structure must be present.

    If this fails: browser evidence has no committed home — reports
    will be lost or stored inconsistently.
    """
    for d in ["browser-tests/scenarios", "browser-tests/reports", "browser-tests/artifacts"]:
        assert (ROOT / d).is_dir(), f"{d}/ must exist"
