# Strata

**Named after geological strata** — the distinct layers that together tell the complete story of the earth.

[中文文档](README.zh.md)

> **Know that it works. Not just that it was written.**

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

**Static** — where architectural invariants live. Patterns that must never appear. Files that must always exist. Handlers that must cover every case. No server, no imports, pure text and AST. If a new route bypasses auth, static catches it before the server ever starts.

**Unit** — deterministic logic, fast and without flakiness. Every test answers one question beyond "does it pass": *what breaks in the product if this test fails?* That answer is in the docstring. A test without a why gets deleted when it fails instead of fixed.

**Browser** — the product, treated as a black box. No importing internals. The driver acts as a user. Evidence gets committed. A scenario run without committed evidence didn't happen.

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
| Invariant | A structural fact that must always hold, checked in `static.py` |
| Tracking file | A markdown file with a test plan, moved from `todo/` to `done/` |
| Scenario | A markdown file describing a user flow — driver-independent |
| Driver | The tool that executes a scenario: `playwright`, `browser-use`, `claude-in-chrome` |
| Evidence | What proves a scenario passed — text committed, binaries local |
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
