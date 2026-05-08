# Scenario Format

One markdown file per scenario under `browser-tests/scenarios/`.

A scenario describes what to test and what evidence to collect. It must not encode driver-specific logic.

## Template

```markdown
---
name: scenario-name
setup: default
tags: [auth, files, routing]
surfaces: [dom, network, server_logs, screenshots]
fixtures: [existing_user]
actions: [login, navigate, submit_form]
waits: [page_load, api_response]
---

# scenario-name

## Purpose
One sentence: the specific product behavior this scenario verifies.

## User Flow
1. User opens the app.
2. User does X.
3. User observes Y.

## Fixtures
- Describe the starting state required before step 1.

## Actions
- Driver-independent user operations to perform.

## Wait / Settling
- Named async convergence points with timeout expectations.

## UI Observations
- What the user should see in the browser (DOM, layout, text).

## Network Observations
- HTTP response bodies, status codes, WebSocket frames to capture.

## Server-Side Observations
- Log lines or trace events showing the backend received the expected request.

## State Observations
- Database rows or filesystem files to verify (secondary confirmation).

## Asserts
- Explicit pass/fail decisions.
  - pass: DOM shows X
  - pass: API returns status 200 with body Y
  - fail: server log shows error Z

## Report
- Required committed files under `browser-tests/reports/scenario-name/<run-id>/`:
  - report.md
  - report.json
  - dom.txt (or dom.json)
  - network.json
  - server.log
- Local screenshots under `browser-tests/artifacts/scenario-name/<run-id>/`.

## Cleanup
- State left behind or cleaned up after the run.
```

## Rules

- **One scenario per file.** File name matches `name`: `user-login` → `user-login.md`.
- **Driver-independent.** Actions are user-level operations, not library calls.
- **Explicit asserts.** "DOM shows X" or "status 200" — not "looks correct".
- **Surfaces declared in frontmatter.** List only surfaces you will actually observe.
- **Committed text evidence only.** Images/videos go to `artifacts/`, not `reports/`.
- **No implementation details.** Do not reference internal function names or database schema.

## Frontmatter Fields

| Field | Values | Description |
|-------|--------|-------------|
| `name` | kebab-case | Matches the file name |
| `setup` | `default`, `seeded`, `empty` | Fixture category |
| `tags` | list of strings | Risk areas: `auth`, `routing`, `files`, `forms`, `permissions`, `startup` |
| `surfaces` | list of strings | `dom`, `screenshots`, `network`, `server_logs`, `database`, `filesystem` |
| `fixtures` | list of strings | `fresh_user`, `existing_user`, `existing_data`, `multi_account` |
| `actions` | list of strings | High-level user actions performed |
| `waits` | list of strings | Named async convergence points |

## Naming Convention

Use descriptive kebab-case names that describe the behavior, not the implementation:

```
user-login.md          ✓
auth.spec.md           ✗ (spec suffix belongs to test code, not scenarios)
TestUserLogin.md       ✗ (no PascalCase)
login_flow.md          ✗ (use hyphens, not underscores)
```
