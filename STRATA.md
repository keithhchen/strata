# Harness

---

## Development Principles

These principles apply to every change, in every layer.

| Principle | Rule |
|-----------|------|
| **Occam's Razor** | Don't add what isn't necessary. |
| **Tests first** | Write the failing test before the implementation. |
| **Full validation** | Every change runs every affected test. |
| **No silent exceptions** | Every exception is logged, re-raised, or explicitly justified. |
| **Reduce complexity** | Less code, fewer concepts, fewer moving parts. |
| **Lateral thinking** | Nothing is a special case — find the parallel entities. |
| **Error-first** | Design the failure paths before the happy path. |

**Occam's Razor.** A simpler design that works is better than a complex design that also works. When you feel the urge to abstract, generalize, or future-proof, ask whether the problem you're solving actually exists yet.

**Tests first.** This isn't ceremony — it's how you know the test checks what you think it checks. A test written after the implementation tends to confirm the implementation, not validate behavior.

**Full validation.** The cost of skipping is discovering a broken invariant three PRs later with no clear blame.

**No silent exceptions.** `except Exception: pass` is evidence destruction. Silent failures make production debugging impossible.

**Always reduce complexity.** A feature that requires three new abstractions is a design smell. Reframe the problem until the implementation feels obvious.

**Lateral thinking.** When making a change, ask: what are the parallel entities? Should they all change together? Special-casing is how codebases accumulate inconsistency.

**Error-first thinking.** Before implementing the happy path, enumerate the failure modes. What are the inputs that break this? What happens when the external call fails?

---

## The Three-Layer Pyramid

```
              ╱╲
             ╱  ╲           browser
            ╱ B  ╲          product as black box
           ╱      ╲         minutes · running product
          ╱────────╲
         ╱          ╲       unit
        ╱     U      ╲      pure logic
       ╱              ╲     seconds · no server
      ╱────────────────╲
     ╱                  ╲   static
    ╱        S           ╲  structural invariants
   ╱                      ╲ milliseconds · no dependencies
  ╱────────────────────────╲
```

The pyramid isn't about quantity — it's about **cost and question type**.

| Layer | Question | Speed | Needs |
|-------|----------|-------|-------|
| `static` | Does the structure hold? | < 0.3s | nothing |
| `unit` | Does the logic work? | < 5s | no server |
| `browser` | Does the product work? | minutes | running product |

**Why static exists.** Some bugs are visible from source text alone — a missing handler, a silent exception, a corrupted template. These can be caught in 0.3 seconds with zero infrastructure. Every team that skips this layer is running a build that can silently rot at the structural level.

**Why unit exists.** Logic that doesn't require I/O can be tested deterministically, fast, and without flakiness. The mistake is over-mocking — unit tests that mock so much they prove nothing.

**Why browser exists.** "Does the login form actually log the user in?" is not answerable by reading code. The browser layer tests the product as a product, with a real browser, against a real server, with committed evidence.

### Layer Selection

```
  What are you testing?
         │
         ├── Structural fact, pattern, file existence, dependency pin?
         │         └──► static
         │
         ├── Pure function, parser, state machine, no I/O?
         │         └──► unit
         │
         └── API, UI, WebSocket, database state, file state?
                   └──► browser

  Affects multiple layers? → test in all of them.
  Not sure? → use the cheapest layer that can answer the question.
```

---

## Scenario Design

A scenario is a markdown file. It is content, not code.

Executable test code couples the test to a specific library, a specific API, a specific version. A markdown scenario describes *what a user does and what the product must prove* — and that description outlasts any particular tool.

### The Pipeline

```
 Fixtures ──► Actions ──► Wait/Settling ──► Sensors ──► Asserts ──► Report ──► Cleanup
     │            │              │              │           │          │
  starting     user-level    named async    observe     pass/fail  commit     isolate
  state        operations    convergence    surfaces    decisions  evidence   state
```

### The Structure

```markdown
---
name: user-login
tags: [auth, routing]
surfaces: [dom, network, server_logs]
fixtures: [fresh_user]
actions: [open_app, fill_form, submit]
waits: [page_load, api_response]
---

## Purpose        ← one sentence: the behavior under test
## User Flow      ← steps as a user would perform them
## Fixtures       ← required starting state
## Actions        ← driver-independent operations
## Wait/Settling  ← named async convergence points with timeouts
## UI Observations
## Network Observations
## Server-Side Observations
## State Observations  ← DB, filesystem — secondary confirmation
## Asserts        ← explicit pass/fail, not "looks correct"
## Report         ← required committed files and paths
## Cleanup        ← what state is left behind or cleaned up
```

**Key rules:**
- One scenario per file. File name matches the `name` field.
- Actions are user-level: "Click the submit button" not `page.click('#submit')`.
- Asserts are specific: "DOM shows `Welcome, Alice`" not "user is logged in."
- Every run produces a committed `report.md` and `report.json`.

Full spec: [skills/browser/references/scenario-format.md](skills/browser/references/scenario-format.md)

---

## Driver

A driver executes a scenario against the running product. Three peer drivers:

| Driver | Mode | Best for |
|--------|------|----------|
| `playwright` | Scripted | CI, deterministic automation |
| `browser-use` | AI-driven | Natural language actions |
| `claude-in-chrome` | Interactive | Debugging, visual inspection |

**Drivers are interchangeable.** The scenario describes *what*; the driver handles *how*. Switching drivers must not require rewriting scenarios or changing evidence expectations.

### Evidence Paths

```
browser-tests/
├── reports/                         ← committed to git
│   └── <scenario>/
│       └── <run-id>/
│           ├── report.md            text summary
│           ├── report.json          machine-readable
│           ├── dom.txt              DOM snapshot
│           ├── network.json         HTTP / WS responses
│           └── server.log           backend log excerpt
│
└── artifacts/                       ← gitignored (binary only)
    └── <scenario>/
        └── <run-id>/
            └── screenshot.png
```

A scenario run without committed text evidence didn't happen.

Full taxonomy: [skills/browser/references/evidence-taxonomy.md](skills/browser/references/evidence-taxonomy.md)

---

## Development Paradigm

### Tracking File → Worktree → Loop

Every change starts with a tracking file that contains a test plan. The file is committed before the worktree is created — untracked files don't travel with worktrees.

```
  features/todo/                     issues/todo/
       │                                  │
       │  cp TEMPLATE.md                  │  cp TEMPLATE.md
       │  fill test plan                  │  fill root cause
       │  git commit                      │  git commit
       ▼                                  ▼
  git worktree add ../proj-feat-x    git worktree add ../proj-fix-y
       │                                  │
       └──────────────┬───────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  write test   │  ← RED
              │  (fails)      │
              └──────┬────────┘
                     │
              ┌──────▼────────┐
              │  write code   │  ← GREEN
              │  (passes)     │
              └──────┬────────┘
                     │
              ┌──────▼────────────────────┐
              │  ./strata/testing.sh all │
              │  browser scenario + report│
              └──────┬────────────────────┘
                     │
              ┌──────▼────────┐
              │  todo/ ──►    │
              │  done/        │  ← fill in results
              └──────┬────────┘
                     │
                     ▼
                  open PR
```

### Worktree Setup

```bash
# 1. commit tracking file first
git add features/todo/my-feature.md
git commit -m "track: open feature my-feature"

# 2. create worktree
git worktree add ../my-project-feat-my-feature -b feat/my-feature

# 3. symlink .env (gitignored, won't travel)
cd ../my-project-feat-my-feature
ln -sf ../my-project/.env .env
```

Multiple worktrees can be open simultaneously. Changes in one don't affect another.

---

## Running Tests

```bash
./strata/testing.sh static    # < 0.3s — structural invariants
./strata/testing.sh unit      # < 5s  — pure logic
./strata/testing.sh all       # static + unit
```

Browser tests use the `browser` skill, not this script. Start the product, select a scenario, choose a driver, commit the evidence.

---

## Completion Standard

```
 ✓  Tracking file records which layers apply
 ✓  Tests written before product code (red first)
 ✓  ./strata/testing.sh all passes
 ✓  Browser scenarios have committed evidence in browser-tests/reports/
 ✓  Tracking file moved to done/ with results filled in
 ✓  Skipped browser coverage has a written reason recorded
```
