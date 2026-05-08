# Strata

**Named after geological strata** — the distinct layers that together tell the complete story of the earth.

[中文文档](README.zh.md)

> **Know that it works. Not just that it was written.**

---

AI can write code faster than you can review it. That's the problem.

Not the writing — the knowing. Knowing whether what was written actually works. Knowing whether it broke something else. Knowing, with evidence, that the feature is done and not just "done."

Strata is a testing methodology for this reality. Three layers. A decision rule for choosing between them. And AI coding assistant skills that encode the methodology so your agents make the same calls your best engineer would.

---

## The Three Layers

The core insight is that "does this work?" is actually three different questions at three different costs.

**Static** asks: *does the structure hold?* No server. No imports. Pure text and AST analysis. Under 0.3 seconds. This is where architectural invariants live — patterns that must never appear, files that must always exist, handlers that must cover every case. If a new route bypasses auth, static catches it before the server ever starts.

**Unit** asks: *does the logic work?* No server, mocked externals, under 5 seconds. Pure functions, parsers, state machines, auth rules. Every unit test answers one question beyond "does it pass": *what breaks in the product if this test fails?* That answer is in the docstring. A test without a why gets deleted when it fails instead of fixed.

**Browser** asks: *does the product work?* The running product, treated as a black box, driven by a real browser. No importing internals. No mocking the thing you're trying to test. The driver acts as a user. Evidence — DOM snapshots, logs, API responses — gets committed. Screenshots stay local. A scenario run without committed evidence didn't happen.

---

## Design Choices Worth Knowing

**Drivers are interchangeable.** A scenario is a markdown file. Playwright, browser-use, and Claude in Chrome are peer implementations of the same contract. The scenario outlives any particular tool.

**Evidence taxonomy is strict.** Text evidence (DOM, logs, JSON) is committed to `browser-tests/reports/`. Binary evidence (screenshots, video) lives in `browser-tests/artifacts/`, gitignored. This keeps the repo lean without losing reproducibility.

**Tracking files are contracts.** Before writing code, you write a tracking file with a test plan. It moves from `todo/` to `done/` when tests pass and evidence exists. The intent and the proof live next to the code.

**Skills are executable methodology.** The three skills — `static`, `unit`, `browser` — are not documentation. They're instructions that run inside your AI assistant. When an agent invokes the static skill, it makes the same layer-selection decisions a senior engineer would. The methodology travels with the repo.

---

## Key Concepts

| Concept | What it is |
|---------|-----------|
| Layer | `static`, `unit`, or `browser` — each answers a different question |
| Invariant | A structural fact that must always hold, checked in `static.py` |
| Tracking file | A markdown file with a test plan, moved from `todo/` to `done/` when done |
| Scenario | A markdown file describing a user flow — driver-independent |
| Driver | The tool that executes a scenario: `playwright`, `browser-use`, `claude-in-chrome` |
| Evidence | What proves a scenario passed — text committed, binaries local |
| Skill | Methodology encoded for an AI coding assistant |

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

Full adoption guide: [HARNESS.md](HARNESS.md)

---

## Reference

- [HARNESS.md](HARNESS.md) — layer reference and adoption guide
- [Scenario format](skills/browser/references/scenario-format.md)
- [Evidence taxonomy](skills/browser/references/evidence-taxonomy.md)
- [Browser model](skills/browser/references/harness-model.md)
