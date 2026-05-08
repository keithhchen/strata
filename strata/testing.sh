#!/usr/bin/env bash
# testing.sh — deterministic static/unit test runner
#
# Usage:
#   ./strata/testing.sh static
#   ./strata/testing.sh unit
#   ./strata/testing.sh all
#
# Layers:
#   static  — AST-level invariant checks, no server needed
#   unit    — pure logic, mocked externals, fast
#   browser — scenario-driven, requires running product; use the browser skill
#
# Configure FRONTEND_DIR below if your project has a frontend test suite.
# Set it to an empty string to skip frontend unit tests.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAYER="${1:-all}"

# Set to your frontend directory (e.g. "frontend" or "client"), or "" to skip.
FRONTEND_DIR="${FRONTEND_DIR:-}"

[ -f "$ROOT/.env" ] && set -a && source "$ROOT/.env" && set +a

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

pass()    { echo -e "${GREEN}✓${NC} $1"; }
fail()    { echo -e "${RED}✗${NC} $1"; }
section() { echo -e "\n${BOLD}── $1 ──${NC}"; }

START=$(date +%s)

run_static() {
  section "Static"
  cd "$ROOT"
  if python3 -m pytest strata/static.py -q --tb=short 2>&1; then
    pass "Static passed"
  else
    fail "Static FAILED"; return 1
  fi
}

run_unit() {
  section "Unit (backend)"
  cd "$ROOT"
  if python3 -m pytest strata/unit.py -q --tb=short 2>&1; then
    pass "Unit passed"
  else
    fail "Unit FAILED"; return 1
  fi

  if [ -n "$FRONTEND_DIR" ] && [ -d "$ROOT/$FRONTEND_DIR" ]; then
    section "Unit (frontend)"
    cd "$ROOT/$FRONTEND_DIR"
    if npm test 2>&1; then
      pass "Frontend unit passed"
    else
      fail "Frontend unit FAILED"; return 1
    fi
    cd "$ROOT"
  fi
}

case "$LAYER" in
  static) run_static ;;
  unit)   run_unit ;;
  all)    run_static && run_unit ;;
  *)
    echo "Usage: $0 [static|unit|all]"
    exit 1
    ;;
esac

ELAPSED=$(( $(date +%s) - START ))
echo ""
echo -e "${GREEN}${BOLD}Tests passed${NC} (${ELAPSED}s)"
