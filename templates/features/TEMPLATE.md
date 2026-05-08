# Feature: [Title]

**Created:** YYYY-MM-DD  
**Status:** todo | in-progress | done

---

## Description

What this feature does and what problem it solves.

---

## Test Plan

> Fill this in before writing any code. Tests come first.

**Layers affected:**

- [ ] static — what structural invariant needs to be enforced or checked?
- [ ] unit — what pure logic needs to be tested?
- [ ] browser — what user flow needs to be verified end-to-end?

**Static checks to add** (if applicable):
```
strata/static.py:
- 
```

**Unit tests to add** (if applicable):
```
strata/unit.py:
- 
```

**Browser scenario** (if applicable):
```
Scenario name:
Setup: default | seeded | empty
Driver preference: playwright | browser-use | claude-in-chrome
User flow:
  1. 
Observations:
  - UI:
  - Network:
  - Server logs:
Asserts:
  - pass: 
  - fail: 
```

**Run verification:**
```bash
./strata/testing.sh static
./strata/testing.sh unit
# browser: use the browser skill with browser-tests/scenarios/<name>.md
```

---

## Design Notes

Brief implementation approach, 3–5 lines max.

Questions to answer before coding:
- Who consumes this? User-facing or internal?
- Does it involve persistent state? Who owns it?
- Does it affect any existing behavior? What could break?

---

## Test Results

> Fill this in after completing the implementation.

```
./strata/testing.sh static   →  pass | fail
./strata/testing.sh unit     →  pass | fail
browser report                →  browser-tests/reports/<scenario>/<run-id>/report.md
```

**Issues found during testing:**

**Conclusion:**
