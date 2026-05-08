# Strata

**Named after geological strata** — the distinct layers that together tell the complete story of the earth.

Three test layers. Each answers a different question. Together they prove your software works.

| Layer | Question | Cost | Needs |
|-------|----------|------|-------|
| **static** | Does the structure hold? | < 0.3s | nothing |
| **unit** | Does the logic work? | < 5s | no server |
| **browser** | Does the product work? | minutes | running product |

AI coding assistant skills make the methodology repeatable — for human developers and agents alike.

---

## Quick Start

### Option A: New project from template

```bash
gh repo create my-app --template your-org/strata
cd my-app
```

### Option B: Add to an existing project

```bash
# 1. Copy harness structure
cp -r path/to/strata/harness         ./harness
cp -r path/to/strata/browser-tests   ./browser-tests
cp -r path/to/strata/templates/features ./features
cp -r path/to/strata/templates/issues   ./issues

# 2. Add .gitignore rules
cat path/to/strata/gitignore.snippet >> .gitignore

# 3. Install skills for your AI assistant
cp -r path/to/strata/skills/static  .claude/skills/static
cp -r path/to/strata/skills/unit    .claude/skills/unit
cp -r path/to/strata/skills/browser .claude/skills/browser

# 4. Verify the starter tests run
./harness/testing.sh all
```

---

## Using Strata in a Web App

This walkthrough uses a React + Express + PostgreSQL project as the example.

### Step 1: Define your invariants

Before writing test code, write down what must always be true about your project's *structure*:

> "All Express routes must use the auth middleware."  
> "Every API handler must be registered in the router index."  
> "No `console.log` in production source files."  
> "`.env.example` must document every env var the app reads."

These structural facts belong in `harness/static.py`. They can be checked without starting a server.

### Step 2: Write failing static tests

Open `harness/static.py` and add your invariants:

```python
def test_routes_use_auth_middleware():
    """All route files must import and apply authMiddleware.

    If this fails: an unprotected route was added. Every endpoint
    must verify the JWT before processing the request.
    """
    for path in ROOT.glob("src/routes/*.js"):
        src = path.read_text()
        assert "authMiddleware" in src, \
            f"{path.name} must apply authMiddleware"

def test_no_console_log_in_src():
    """console.log must not appear in production source.

    If this fails: debug output will leak to production logs.
    """
    for path in ROOT.glob("src/**/*.js"):
        assert "console.log" not in path.read_text(), \
            f"Remove console.log from {path}"
```

Run them — make them **red** first if you haven't enforced these yet:

```bash
./harness/testing.sh static
```

### Step 3: Write unit tests for pure logic

Identify logic that works without a database or HTTP server:

- JWT validation
- Input sanitization
- Response shape builders
- Query parameter parsers
- Permission checks

Write one test class per behavior group. Every test documents what breaks in the product if it fails:

```python
class TestJwtValidation:
    def test_expired_token_raises(self):
        """Expired tokens must be rejected.

        If this fails: users with expired sessions bypass auth —
        they can read and modify data they no longer have access to.
        """
        with pytest.raises(TokenExpiredError):
            verify_jwt(make_expired_token())

    def test_valid_token_returns_payload(self):
        """Valid tokens return the decoded payload.

        If this fails: every authenticated request fails — app is unusable.
        """
        payload = verify_jwt(make_valid_token(user_id="u-1"))
        assert payload["user_id"] == "u-1"
```

### Step 4: Install skills and write your first browser scenario

```bash
# Install skills once per project
cp -r path/to/strata/skills/static  .claude/skills/static
cp -r path/to/strata/skills/unit    .claude/skills/unit
cp -r path/to/strata/skills/browser .claude/skills/browser
```

Copy the scenario template and describe your first user flow:

```bash
cp path/to/strata/templates/browser-tests/SCENARIO_TEMPLATE.md \
   browser-tests/scenarios/user-login.md
```

Fill in the sections: what the user does, what you observe, what must be true. The driver (Playwright, browser-use, Claude in Chrome) executes the scenario — the scenario file itself is driver-independent.

### Step 5: Your daily workflow

```
New feature arrives:
  1. Create features/todo/my-feature.md — fill in the test plan before coding
  2. git add + commit the tracking file
  3. git worktree add (or branch) for isolation
  4. Write tests → make them red
  5. Write code → make them green
  6. ./harness/testing.sh all
  7. Run browser scenario, commit the report to browser-tests/reports/
  8. Move tracking file: features/todo/ → features/done/

Bug arrives:
  Same flow, using issues/todo/ instead of features/todo/
```

---

## Layer Selection

```
String pattern, file existence, structural convention, dependency pin?
  → static

Pure function, parser, state machine, deterministic event mapping?
  → unit

API response, UI rendering, database state, file state, WebSocket event?
  → browser

Change affects multiple layers?
  → test in every affected layer
```

When in doubt: **start with the cheapest layer that can answer the question.**

---

## AI Skills

Skills are instructions for AI coding assistants (Claude Code, Codex, Cursor, etc.) that encode this methodology. Once installed, your AI assistant knows how to:

- Decide which test layer a new test belongs to
- Write a static invariant check using AST or text analysis
- Structure a unit test class with WHY docstrings
- Select and execute a browser scenario
- Collect and commit evidence to the right paths

**Installing for Claude Code:**

```bash
cp -r skills/static  .claude/skills/static
cp -r skills/unit    .claude/skills/unit
cp -r skills/browser .claude/skills/browser
```

**Installing for Codex:**

```bash
cp -r skills/static  .codex/skills/static
cp -r skills/unit    .codex/skills/unit
cp -r skills/browser .codex/skills/browser
```

For other assistants, copy the `skills/` directory wherever your assistant loads tool documentation.

---

## Project Structure

After setup your project has:

```
your-project/
├── harness/
│   ├── static.py          # Structural invariant tests — adapt to your project
│   ├── unit.py            # Pure logic tests — adapt to your project
│   └── testing.sh         # ./harness/testing.sh [static|unit|all]
│
├── browser-tests/
│   ├── scenarios/         # One .md file per user flow
│   ├── reports/           # Committed text evidence (DOM, logs, JSON, report.md)
│   └── artifacts/         # Local screenshots/videos (gitignored)
│
├── features/
│   ├── todo/              # Tracking files for features in progress
│   └── done/              # Closed features (with test results filled in)
│
└── issues/
    ├── todo/              # Tracking files for bugs in progress
    └── done/              # Closed bugs
```

---

## Completion Standard

A change is complete only when:

1. The tracking file records which layers apply
2. Tests were written before product code (red first)
3. `./harness/testing.sh all` passes
4. Browser scenarios have committed report evidence under `browser-tests/reports/`
5. Any skipped browser coverage has a written reason and residual risk recorded

---

[中文文档](README.zh.md)

## Reference

- [HARNESS.md](HARNESS.md) — Core layer reference
- [Scenario format](skills/browser/references/scenario-format.md)
- [Evidence taxonomy](skills/browser/references/evidence-taxonomy.md)
- [Browser model](skills/browser/references/harness-model.md)
