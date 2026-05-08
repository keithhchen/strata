# Harness

---

## Development Principles

These principles apply to every change, in every layer.

**Occam's Razor.** Don't add what isn't necessary. A simpler design that works is better than a complex design that also works. When you feel the urge to abstract, generalize, or future-proof, ask whether the problem you're solving actually exists yet.

**Tests first.** Write the failing test before writing the implementation. This isn't ceremony — it's how you know the test actually checks what you think it checks. A test written after the implementation tends to be a test that confirms the implementation, not one that validates behavior.

**Full validation.** Every change runs every affected test. Not just the tests near the change. The cost of skipping is discovering a broken invariant three PRs later with no clear blame.

**No silent exceptions.** `except Exception: pass` is not error handling. It's evidence destruction. Every exception must be logged, re-raised, or explicitly justified. Silent failures make production debugging impossible.

**Always reduce complexity.** When adding a feature, ask whether it can be done with less — less code, fewer concepts, fewer moving parts. A feature that requires three new abstractions is a design smell. Reframe the problem until the implementation feels obvious.

**Lateral thinking.** When making a change, don't treat it as a special case. Ask: what are the parallel entities here? Should they all change together? Special-casing is how codebases accumulate inconsistency.

**Error-first thinking.** Before implementing the happy path, enumerate the failure modes. What are the inputs that break this? What happens when the external call fails? What happens when the state is wrong? Design the error paths before the success path.

---

## The Three-Layer Pyramid

```
         ▲
        /B\        browser — product as black box
       /   \       minutes, requires running product
      /─────\
     /   U   \     unit — pure logic
    /         \    seconds, no server
   /───────────\
  /     S       \  static — structural invariants
 /               \ milliseconds, no dependencies
/─────────────────\
```

The pyramid isn't just about quantity — it's about **cost and question type**.

| Layer | Question | Speed | Dependencies |
|-------|----------|-------|--------------|
| static | Does the structure hold? | < 0.3s | none |
| unit | Does the logic work? | < 5s | no server |
| browser | Does the product work? | minutes | running product |

**Why static exists.** Some bugs are visible from source text alone — a missing handler, a silent exception, a corrupted template. These can be caught in 0.3 seconds with zero infrastructure. Every team that skips this layer is running a build that can silently rot at the structural level.

**Why unit exists.** Logic that doesn't require I/O can be tested deterministically, fast, and without flakiness. The mistake is over-mocking — unit tests that mock so much they prove nothing. Unit tests should cover logic that actually lives in functions, not integration behavior.

**Why browser exists.** Some behaviors cannot be verified from source. "Does the login form actually log the user in and redirect to the dashboard?" is not answerable by reading code. The browser layer exists to test the product as a product, with a real browser, against a real server, with committed evidence.

**The decision rule:**
```
Structural fact, pattern check, file existence?
  → static

Pure function, parser, state machine, no I/O?
  → unit

API, UI, WebSocket, file state, database state?
  → browser
```

When in doubt, go to the cheapest layer that can answer the question.

---

## Scenario Design

A scenario is a markdown file. It is content, not code.

This is a deliberate choice. Executable test code couples the test to a specific library, a specific API, a specific version. A markdown scenario describes *what a user does and what the product must prove* — and that description outlasts any particular tool.

**The structure:**

```markdown
---
name: user-login
tags: [auth, routing]
surfaces: [dom, network, server_logs]
fixtures: [fresh_user]
actions: [open_app, fill_form, submit]
waits: [page_load, api_response]
---

## Purpose
One sentence: the behavior under test.

## User Flow
Steps as a user would perform them.

## Fixtures
Required starting state.

## Actions
Driver-independent user operations.

## Wait / Settling
Named async convergence points with timeouts.

## UI Observations
What should be visible in the browser.

## Network Observations
HTTP responses, status codes, WebSocket frames.

## Server-Side Observations
Log lines proving the backend received and processed the request.

## State Observations
Database rows, filesystem files — secondary confirmation.

## Asserts
Explicit pass/fail decisions. Not "looks correct" — specific evidence.

## Report
Required committed files and their paths.

## Cleanup
What state is left behind or cleaned up.
```

**Key rules:**
- One scenario per file. File name matches the `name` field.
- Actions are user-level. "Click the submit button" not `page.click('#submit')`.
- Asserts are specific. "DOM shows `Welcome, Alice`" not "user is logged in."
- Every scenario run must produce a `report.md` and `report.json`, committed.

Full spec: [skills/browser/references/scenario-format.md](skills/browser/references/scenario-format.md)

---

## Driver

A driver is the tool that executes a scenario. Three peer drivers:

| Driver | Best for |
|--------|----------|
| `playwright` | Deterministic automation, CI |
| `browser-use` | AI-driven execution, natural language |
| `claude-in-chrome` | Interactive debugging, visual inspection |

The critical design decision: **drivers are interchangeable**. A scenario must not assume a specific driver. The scenario describes *what*; the driver handles *how*.

Switching from Playwright to browser-use must not require rewriting scenarios. The evidence a scenario demands — DOM snapshots, network responses, server logs — must be collectable by any driver.

Evidence has two homes:
- `browser-tests/reports/<scenario>/<run-id>/` — text evidence, committed to git
- `browser-tests/artifacts/<scenario>/<run-id>/` — binary evidence (screenshots, video), gitignored

A scenario run without committed text evidence didn't happen as far as the team is concerned.

Full evidence taxonomy: [skills/browser/references/evidence-taxonomy.md](skills/browser/references/evidence-taxonomy.md)

---

## Development Paradigm

### The Tracking File

Every change — feature or bug — starts with a tracking file.

```bash
# Feature
cp templates/features/TEMPLATE.md features/todo/my-feature.md

# Bug
cp templates/issues/TEMPLATE.md issues/todo/my-bug.md
```

The tracking file has a test plan section. Fill it before writing code. The test plan answers: which layers are affected, what tests need to be added, what browser scenarios need to run.

**The tracking file must be committed before creating a worktree.** Untracked files don't travel with worktrees. A tracking file created after the worktree won't be there.

### The Worktree

Each feature or bug gets its own git worktree, not a branch on the same checkout.

```bash
git add features/todo/my-feature.md && git commit -m "track: open feature my-feature"
git worktree add ../my-project-feat-my-feature -b feat/my-feature
```

Worktrees let you work on multiple changes simultaneously without stashing or context switching. Each worktree is isolated — changes in one don't affect another.

`.env` is gitignored and won't travel with the worktree. Symlink it:

```bash
ln -sf ../my-project/.env .env
```

### The Loop

```
1. Create tracking file with test plan
2. git add + commit tracking file
3. git worktree add (isolated branch)
4. Write the test → make it red
5. Write the implementation → make it green
6. ./harness/testing.sh all
7. Run browser scenario if applicable → commit report
8. Move tracking file: todo/ → done/ (fill in results)
9. Open PR from worktree branch
```

The loop is the same for features and bugs. The only difference is which directory the tracking file goes in.

---

## Running Tests

```bash
./harness/testing.sh static    # structural invariants only
./harness/testing.sh unit      # pure logic only
./harness/testing.sh all       # static + unit
```

Browser tests use the `browser` skill, not this script. Start the product stack, select a scenario, choose a driver, commit the evidence.

---

## Completion Standard

A change is complete when:

1. Tracking file records which layers apply
2. Tests were written before product code (red first)
3. `./harness/testing.sh all` passes
4. Browser scenarios have committed evidence in `browser-tests/reports/`
5. Tracking file moved to `done/` with results filled in
6. Skipped browser coverage has a written reason and residual risk recorded
