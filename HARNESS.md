# Harness — Core Reference

## Mental Model

```
full testing environment = static + unit + browser
```

No layer substitutes for another. Each answers a different question at a different cost.

## Layers

| Layer | Purpose | Entry point | Needs |
|-------|---------|-------------|-------|
| static | Code structure, forbidden patterns, file conventions, dependency policy | `harness/static.py` | nothing |
| unit | Pure backend/frontend logic, parsers, reducers, state machines | `harness/unit.py` and frontend tests | nothing |
| browser | Product-black-box user workflows through real browser, HTTP/WS, logs | `browser-tests/scenarios/*.md` + driver | running product |

Static and unit are deterministic scripts. Browser is scenario content plus a driver plus committed report evidence.

## Running Static and Unit

```bash
./harness/testing.sh static
./harness/testing.sh unit
./harness/testing.sh all     # static + unit
```

## Running Browser

1. Start the product stack (Docker, local server, or staging).
2. Select or create a scenario file in `browser-tests/scenarios/`.
3. Choose a driver: `playwright`, `browser-use`, or `claude-in-chrome`.
4. Execute the scenario as a user against the running product.
5. Commit text evidence under `browser-tests/reports/<scenario>/<run-id>/`.
6. Leave screenshots and videos under `browser-tests/artifacts/<scenario>/<run-id>/` (gitignored).

## Test Selection

```
String pattern, file existence, structural convention, dependency pin?
  → static

Pure function, parser, reducer, state machine, deterministic mapping?
  → unit

API response, WebSocket event, UI rendering, file state, database state?
  → browser

Behavior spans multiple layers?
  → test in every affected layer
```

## Skills

Three AI coding assistant skills live under `skills/`:

| Skill | Use |
|-------|-----|
| `skills/static` | Selecting and writing static invariant checks |
| `skills/unit` | Selecting and writing unit tests |
| `skills/browser` | Selecting scenarios, choosing drivers, collecting evidence |

Deploy to your AI assistant's skills directory. See each skill's `SKILL.md` for details.

## Browser Scenario Format

Each scenario file must contain:

- YAML frontmatter: `name`, `setup`, `tags`, `surfaces`, `fixtures`, `actions`, `waits`
- `## Purpose`
- `## User Flow`
- `## Fixtures`
- `## Actions`
- `## Wait / Settling`
- `## Product Observations`
- `## UI Observations`
- `## Network Observations`
- `## Server-Side Observations`
- `## State Observations`
- `## Asserts`
- `## Report`
- `## Cleanup`

Full rules: `skills/browser/references/scenario-format.md`.

## Completion Standard

A change is complete only when:

- The tracking file records which layers apply
- Tests were written before product code where feasible (red first)
- `./harness/testing.sh static` passes
- `./harness/testing.sh unit` passes
- Required browser scenarios have committed report evidence under `browser-tests/reports/`
- Skipped browser coverage has a concrete reason and residual risk recorded in the tracking file
