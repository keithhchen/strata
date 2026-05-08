# Strata

**A test-driven vibe coding methodology.**

*Named after geological strata — the distinct layers that together tell the complete story.*

[中文文档](README.zh.md)

---

AI can write code faster than you can review it. That's the problem.

Not the writing — the knowing. Knowing whether what was written actually works. Knowing whether it broke something else. Knowing, with evidence, that the feature is done and not just "done."

Strata is a testing methodology and project template for AI-assisted development. Three layers. A decision rule for choosing between them. AI coding assistant skills that encode the methodology so your agents make the same calls your best engineer would.

---

## The Three Layers

```
              ╱╲
             ╱  ╲           browser
            ╱ B  ╲          product as black box · minutes
           ╱──────╲
          ╱   U    ╲        unit
         ╱          ╲       pure logic · seconds
        ╱────────────╲
       ╱      S       ╲     static
      ╱                ╲    structural invariants · milliseconds
     ╱──────────────────╲
```

| Layer | Question | Speed | Needs |
|-------|----------|-------|-------|
| `static` | Does the structure hold? | < 0.3s | nothing |
| `unit` | Does the logic work? | < 5s | no server |
| `browser` | Does the product work? | minutes | running product |

**Static** — `pytest harness/static.py` with no server, no imports. Regex and AST checks over source files: forbidden patterns, required files, handler coverage. A new route that bypasses auth fails here before the server starts.

**Unit** — `pytest harness/unit.py` with no server, external calls mocked. Pure functions, parsers, state machines. Every test has a docstring that answers: *if this test fails, what breaks in the product?* A test without that answer gets deleted when it fails instead of fixed.

**Browser** — the product runs in Docker. A driver opens a real browser and executes a scenario — a markdown file that describes the user flow, observations, and asserts. Text evidence is committed to `browser-tests/reports/`. A scenario run without committed evidence didn't happen.

---

## Layer Selection

```
  What are you testing?
         │
         ├── Structural fact, pattern, file existence?  ──► static
         │
         ├── Pure function, parser, state machine?      ──► unit
         │
         └── API, UI, database, WebSocket, file state?  ──► browser

  Affects multiple layers? → test in all of them.
```

---

## Scenario

A scenario is a markdown file. It is content, not code. Executable test code couples the test to a specific library and version — a markdown scenario describes *what a user does and what the product must prove*, and that description outlasts any particular driver.

Every scenario has these sections:

```
 Fixtures ──► Actions ──► Wait/Settling ──► Sensors ──► Asserts ──► Report ──► Cleanup
```

| Section | What goes here |
|---------|---------------|
| Purpose | One sentence: the behavior under test |
| User Flow | Steps from the user's perspective |
| Fixtures | Required starting state |
| Actions | Driver-independent operations: "click Submit", not `page.click('#submit')` |
| Wait/Settling | Named async convergence points with timeouts |
| Observations | DOM, network, server logs, database state, filesystem state |
| Asserts | Explicit pass/fail: "DOM shows `Welcome, Alice`" not "user is logged in" |
| Report | Required committed files and their paths |
| Cleanup | State left behind or cleaned up |

---

## Browser

A **driver** executes a scenario against the running product. Three peer drivers — switching drivers does not require rewriting scenarios:

| Driver | Mode | Best for |
|--------|------|----------|
| `playwright` | Scripted | CI, deterministic automation |
| `browser-use` | AI-driven | Natural language actions |
| `claude-in-chrome` | Interactive | Debugging, visual inspection |

Evidence paths after a run:

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

---

## Design Choices

**Drivers are interchangeable.** A scenario is a markdown file. Playwright, browser-use, and Claude in Chrome are peer implementations of the same contract. The scenario outlives any particular tool.

**Evidence taxonomy is strict.** Text evidence (DOM, logs, JSON) is committed. Binary evidence (screenshots, video) stays local, gitignored. Lean repo, full reproducibility.

**Tracking files are contracts.** Every change starts with a tracking file containing a test plan — before any code is written. It moves from `todo/` to `done/` when tests pass and evidence exists.

**Skills are executable methodology.** The three skills — `static`, `unit`, `browser` — are instructions that run inside your AI assistant. When an agent invokes the static skill, it makes the same layer-selection decisions a senior engineer would. The methodology travels with the repo.

---

## Key Concepts

| Concept | What it is |
|---------|-----------|
| Layer | `static`, `unit`, or `browser` — each answers a different question |
| Tracking file | A markdown file with a test plan, moved from `todo/` to `done/` |
| Scenario | A markdown file describing a user flow — driver-independent |
| Driver | The tool that executes a scenario: `playwright`, `browser-use`, `claude-in-chrome` |
| Evidence | Text evidence committed to `browser-tests/reports/`; binaries gitignored locally |
| Skill | Methodology encoded as instructions for an AI coding assistant |

---

## Getting Started

```bash
cp -r path/to/strata/harness            ./harness
cp -r path/to/strata/browser-tests      ./browser-tests
cp -r path/to/strata/templates/features ./features
cp -r path/to/strata/templates/issues   ./issues
cat path/to/strata/gitignore.snippet >> .gitignore

cp -r path/to/strata/skills/static  .claude/skills/static
cp -r path/to/strata/skills/unit    .claude/skills/unit
cp -r path/to/strata/skills/browser .claude/skills/browser

./harness/testing.sh all
```

Full methodology — principles, scenario design, driver contract, development paradigm: **[HARNESS.md](HARNESS.md)**

---

## Reference

- [HARNESS.md](HARNESS.md) — full methodology reference
- [Scenario format](skills/browser/references/scenario-format.md)
- [Evidence taxonomy](skills/browser/references/evidence-taxonomy.md)
- [Browser model](skills/browser/references/harness-model.md)
