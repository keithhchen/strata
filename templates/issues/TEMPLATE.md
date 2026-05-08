# Issue: [Short description of the bug]

**Created:** YYYY-MM-DD  
**Status:** todo | in-progress | done

---

## Symptom

What the user or developer observes. Be specific: what happened, what was expected, how to reproduce.

---

## Root Cause

Fill this in once diagnosed. Leave blank until then.

---

## Test Plan

> Write the failing test before writing the fix.

**Layer:**

- [ ] static — is this a structural violation visible from source?
- [ ] unit — is this a logic error testable in isolation?
- [ ] browser — is this a product behavior failure visible end-to-end?

**Test to add:**
```
File:
Test name:
What it verifies:
Expected: 
Actual:   
```

---

## Fix

Brief description of the fix. Reference the file and line if known.

---

## Test Results

```
./harness/testing.sh static   →  pass | fail
./harness/testing.sh unit     →  pass | fail
browser report                →  browser-tests/reports/<scenario>/<run-id>/report.md
```

**Regression check:**
Did the fix affect any other behavior? Which scenarios were re-run?
