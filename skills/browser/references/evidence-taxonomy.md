# Evidence Taxonomy

Every browser scenario run produces two kinds of artifacts. The distinction is critical for keeping the repository clean while preserving reproducibility.

## Committed Evidence (`browser-tests/reports/`)

Text-based. Must be committed to git after every scenario run that matters.

| File | Description |
|------|-------------|
| `report.md` | Human-readable summary: what was tested, what was observed, pass/fail |
| `report.json` | Machine-readable summary: same content as `report.md`, JSON format |
| `dom.txt` / `dom.json` | DOM snapshot at key moments (after login, after submit, after result) |
| `network.json` | HTTP responses, status codes, request/response bodies |
| `ws-trace.jsonl` | WebSocket frame trace |
| `server.log` | Backend log excerpt showing requests received and errors |
| `database-snapshot.json` | Selected rows confirming state changes (secondary) |
| `filesystem-observation.json` | File presence/absence in the workspace (secondary) |

**Why commit text evidence?** A failing browser scenario with no committed report is unfalsifiable — nobody can tell if it passed, failed, or was never run. Text evidence is the audit trail.

## Local Artifacts (`browser-tests/artifacts/`)

Binary or large. Kept on the developer's machine, never committed.

| File | Description |
|------|-------------|
| `*.png`, `*.jpg`, `*.webp` | Screenshots captured during the run |
| `*.mp4`, `*.webm` | Screen recordings |
| Trace archives | Playwright traces, HAR files |

**Why not commit images?** Repository size. A single screenshot is 50–500KB. Fifty scenario runs with five screenshots each is 12–125MB of binary blobs that make `git clone` slow and `git log` noisy.

**The contract:** `report.md` may reference local image paths and checksums. The scenario remains reviewable from committed text evidence alone. If the images are needed, the developer runs the scenario again.

## The Commit Rule

```
Run a browser scenario
  → always write report.md + report.json to reports/
  → commit the reports/ changes with your PR
  → never commit to artifacts/ (gitignored)
```

A PR that changes browser behavior without updated `browser-tests/reports/` is incomplete.

## Path Convention

```
browser-tests/
├── reports/
│   └── <scenario-name>/
│       └── <run-id>/           ← e.g. run-2026-01-15T120000Z or manual-playwright-2026-01-15
│           ├── report.md
│           ├── report.json
│           ├── dom.txt
│           ├── network.json
│           └── server.log
└── artifacts/
    └── <scenario-name>/
        └── <run-id>/
            ├── before-login.png
            └── after-submit.png
```

`<run-id>` format: `manual-<driver>-<date>` or `<timestamp>Z`. Use a timestamp for automated runs, a descriptive name for manual runs.

## gitignore Setup

```gitignore
# Browser harness local visual artifacts
browser-tests/artifacts/**
!browser-tests/artifacts/
!browser-tests/artifacts/.gitkeep

# Reports are committed evidence — override any *.png rule
!browser-tests/reports/**
```

The `!browser-tests/reports/**` override is necessary if your `.gitignore` has a blanket `*.png` rule.
