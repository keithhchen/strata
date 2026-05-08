---
name: scenario-name
setup: default
tags: [tag1, tag2]
surfaces: [dom, network, server_logs, screenshots]
fixtures: [existing_user]
actions: [login, navigate, submit_form]
waits: [page_load, api_response]
---

# scenario-name

## Purpose
One sentence describing the specific product behavior this scenario verifies.

## User Flow
1. User opens the app at the product URL.
2. User performs [action].
3. User observes [result].

## Fixtures
- Describe the required starting state. Example: a registered user with email test@example.com.

## Actions
- Open app
- Log in as existing user
- Navigate to [page]
- Fill in [form field] with [value]
- Click [button]
- Observe [result]

## Wait / Settling
- Wait for page to load (route: /dashboard)
- Wait for API response from POST /api/[endpoint]
- Wait for DOM element [selector] to be visible
- Timeout: 10s per step unless noted

## UI Observations
- [Element] should be visible with text "[expected text]"
- [Page title / heading] should read "[expected]"
- No error banner or error state visible

## Network Observations
- POST /api/[endpoint] returns status 200
- Response body contains [field]: [expected value]
- No 4xx or 5xx responses during the flow

## Server-Side Observations
- Server log shows: `[expected log line]`
- No unhandled exception in server logs

## State Observations
- [Optional] Database row for [entity] exists with [field] = [value]
- [Optional] File [path] exists in the workspace

## Asserts
- pass: UI shows [expected element or text]
- pass: API returns status 200
- pass: Server log confirms request received
- fail: Any 5xx response
- fail: Error message visible in UI
- fail: Expected DOM element missing after settling

## Report
Required committed files under `browser-tests/reports/scenario-name/<run-id>/`:
- `report.md` — human-readable summary
- `report.json` — machine-readable summary
- `dom.txt` — DOM snapshot at key moments
- `network.json` — HTTP responses captured
- `server.log` — relevant server log excerpt

Local screenshots under `browser-tests/artifacts/scenario-name/<run-id>/`.

## Cleanup
- [Describe what state is left behind or cleaned up]
- Example: test user account left in place for subsequent runs
- Example: created record deleted after scenario
