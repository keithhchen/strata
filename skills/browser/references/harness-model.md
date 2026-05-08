# Browser Model

Every browser scenario follows this pipeline:

```
Scenario
→ Fixtures
→ Actions
→ Wait / Settling
→ Driver
→ Sensors
→ Artifacts
→ Asserts
→ Report
→ Cleanup
```

## Scenario

A procedural description of one product behavior. It is content, not executable code. It states what a user does and what product evidence proves success.

## Fixtures

Starting state required before the first user action:

- `fresh_user` — new account, no history
- `existing_user` — account already created
- `existing_data` — seeded records relevant to the scenario
- `empty_state` — explicitly empty workspace or dataset
- `multi_account` — two or more accounts for isolation testing

Prefer fresh, uniquely-named data when possible. Avoid relying on state left by previous tests.

## Actions

User-level operations, driver-independent:

- open app
- register / login / logout
- navigate to page
- fill form field
- click button
- submit form
- upload file
- reload page
- scroll to element
- open/close modal

Drivers implement actions. Scenario files do not encode driver-specific calls.

## Wait / Settling

Every asynchronous transition needs a named wait with a timeout:

- wait for page load / route change
- wait for API response
- wait for WebSocket event
- wait for DOM element visible
- wait for modal content loaded
- wait for backend log line
- wait for file or database state

Fixed sleeps are a last resort. Name the condition, not the duration.

## Drivers

Peer implementations of the same browser contract:

- `playwright` — deterministic, scriptable, CI-friendly
- `browser-use` — AI-driven, natural language actions
- `claude-in-chrome` — interactive, visual, good for debugging

Switching drivers must not change scenario semantics, evidence expectations, or pass/fail assertions.

## Sensors

Observe the product from outside the implementation:

- **DOM** — visible text, element presence, routes, modal content
- **Screenshots** — visual state, layout, overflow, blank areas
- **Network** — HTTP responses, status codes, WebSocket frames, DevTools
- **Server logs** — requests received, auth decisions, errors emitted
- **Database** — row presence/absence (secondary confirmation)
- **Filesystem** — file written or missing (secondary confirmation)

Primary evidence: DOM, screenshots, network, server logs.
Secondary evidence: database, filesystem.

## Artifacts

```
browser-tests/reports/<scenario>/<run-id>/    ← committed to git
browser-tests/artifacts/<scenario>/<run-id>/  ← local only, gitignored
```

Committed: `*.dom.txt`, `*.json`, `*.log`, `report.md`, `report.json`  
Local only: `*.png`, `*.jpg`, `*.mp4`, `*.webm`, trace archives

Reports may reference local image paths, but a scenario must be reviewable from committed text evidence alone.

## Asserts

Hard asserts (scenario fails):
- expected DOM element missing
- expected HTTP status absent
- server error on happy path
- expected file not written

Soft warnings (noted but not blocking):
- framework deprecation warning
- slow but successful wait
- auxiliary sensor unavailable when primary evidence is complete

Every failure must include the missing evidence and the artifact path that would have proven it.

## Report

Each run produces at minimum:

```json
{
  "scenario": "user-login",
  "driver": "playwright",
  "passed": true,
  "fixtures": ["fresh_user"],
  "actions": ["open_app", "fill_login_form", "submit"],
  "asserts": [],
  "warnings": [],
  "artifacts": {
    "dom":         ["browser-tests/reports/user-login/run-id/dom.txt"],
    "network":     ["browser-tests/reports/user-login/run-id/network.json"],
    "server_logs": ["browser-tests/reports/user-login/run-id/server.log"],
    "report_md":   "browser-tests/reports/user-login/run-id/report.md"
  }
}
```

## Cleanup

State isolation is part of the test:

- Use unique identifiers (email, name, slug) when creating data
- Log out or clear session before auth scenarios
- Record whether data was cleaned up or intentionally retained
- Do not let leftover state from a previous run decide pass/fail
