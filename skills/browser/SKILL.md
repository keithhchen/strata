---
name: browser
description: Browser harness layer. Use when a coding agent needs to choose or run browser scenarios against the running product, collect DOM/screenshot/network/log evidence, or validate behavior that cannot be verified from source alone — API responses, UI rendering, WebSocket events, database state, file state.
---

# Browser

Use this skill to evaluate the running product as an external user. The product is a black box — do not import its source code to decide pass/fail.

```
full testing environment = static + unit + browser
```

## Scope

Browser tests verify product behavior through real surfaces:

- UI rendering and interaction
- HTTP API responses
- WebSocket event streams
- Backend log evidence (requests received, routes matched, errors emitted)
- Database state (as secondary confirmation, not primary oracle)
- Filesystem state (file written, file missing)

The product's internal implementation is not the test subject — the observable behavior is.

## Execution

1. Start the product stack.
2. Select a scenario from `browser-tests/scenarios/`.
3. Choose a driver.
4. Execute as a user.
5. Commit text evidence to `browser-tests/reports/<scenario>/<run-id>/`.
6. Keep screenshots/videos local at `browser-tests/artifacts/<scenario>/<run-id>/`.

## Driver Abstraction

Three peer drivers — select by preference:

| Driver | Best for |
|--------|----------|
| `playwright` | Deterministic automation, CI pipelines |
| `browser-use` | AI-driven execution, natural language actions |
| `claude-in-chrome` | Interactive debugging, visual inspection |

Drivers are interchangeable. Switching drivers must not change scenario semantics, evidence expectations, or pass/fail assertions.

## Scenario Selection

1. Read the changed files and the user request.
2. Search `browser-tests/scenarios/` by `tags` and `surfaces` frontmatter.
3. Run every scenario whose trigger matches the change.
4. If no scenario matches, create a new one before testing.
5. Use the narrowest scenario set that covers the risk; add a smoke scenario when auth, routing, or startup changed.

## Evidence Contract

For each scenario, collect evidence from at least two surfaces:

| Surface | What to capture |
|---------|----------------|
| UI | DOM snapshots, visible text, element state, screenshots |
| Network | HTTP response bodies, status codes, WebSocket frames |
| Server logs | Requests received, errors emitted, auth decisions |
| State | Database rows, filesystem files (as confirmation) |

Do not declare pass with only one evidence type unless the scenario explicitly limits surfaces.

## Output Shape

```json
{
  "scenario": "user-login",
  "driver": "playwright",
  "passed": true,
  "report": "browser-tests/reports/user-login/run-2026-01-15T120000Z/report.json",
  "evidence": {
    "dom":             ["browser-tests/reports/user-login/.../dom.txt"],
    "network":         ["browser-tests/reports/user-login/.../network.json"],
    "server_logs":     ["browser-tests/reports/user-login/.../server.log"],
    "screenshots":     ["browser-tests/artifacts/user-login/.../logged-in.png"]
  },
  "failures": []
}
```

## Evidence Paths

```
browser-tests/
├── reports/<scenario>/<run-id>/    ← commit this (text evidence)
│   ├── report.md
│   ├── report.json
│   ├── dom.txt
│   ├── network.json
│   └── server.log
└── artifacts/<scenario>/<run-id>/ ← keep local (gitignored)
    └── screenshot.png
```

See `references/evidence-taxonomy.md` for the full taxonomy.

## Scenario Content Rules

- One scenario per file.
- File name matches `name` field: `user-login` → `user-login.md`.
- Scenarios are driver-independent — no Playwright/browser-use calls in the markdown.
- Actions are user-level: "click Login", "type email", not "page.click('#submit')".
- Asserts are explicit: DOM element present, status 200, log line found — not "looks correct".

See `references/scenario-format.md` for the full format spec.

## Execution Flow

1. Verify the product stack is running.
2. Open the product URL through the chosen driver.
3. Perform the scenario's user steps exactly.
4. After each meaningful UI transition, capture DOM and screenshot evidence.
5. Capture network evidence (DevTools or proxy) during the run.
6. Capture server log evidence from the running container/process.
7. Write `report.md` and `report.json` to `browser-tests/reports/<scenario>/<run-id>/`.
8. Write screenshots/videos to `browser-tests/artifacts/<scenario>/<run-id>/`.
9. State pass/fail with specific evidence references — never prose-only opinion.
