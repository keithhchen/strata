---
name: unit
description: Unit harness layer. Use when a coding agent needs to choose, write, or run deterministic tests for pure logic — parsers, validators, state machines, event mapping, path resolution, and other behavior that requires no running server, database, or browser.
---

# Unit

Use this skill for the unit layer of the full testing environment:

```
full testing environment = static + unit + browser
```

## Scope

Unit tests verify deterministic logic:

- pure functions (parsers, validators, formatters, calculators)
- state machines and reducers
- auth/permission logic that doesn't require a real database
- event/message dispatch and mapping
- path resolution and containment checks
- error-path behavior that can be triggered in isolation
- frontend component logic that can run without a real browser

Unit tests must not depend on a running server, real database, live API keys, or a browser. If a module reads env vars at import time, set deterministic test defaults before importing.

## Execution

```bash
./harness/testing.sh unit
python3 -m pytest harness/unit.py -q --tb=short   # backend only
cd frontend && npm test                             # frontend only
```

## When To Add Unit Coverage

Add or update unit tests when a change depends on:

- function input/output behavior
- exception handling paths
- parsing or serialization correctness
- state transition logic
- path normalization or containment
- event dispatch or mapping

If the behavior requires real HTTP, WebSocket, database state, file polling, or browser rendering, use the browser layer instead or in addition.

## How To Add A Test

1. **Identify the behavior.** One sentence: "Given X input, function Y must produce Z output."

2. **Group by behavior, not by function name.** One class per behavior area.

3. **Write the WHY docstring first.** What breaks in the product if this test fails?

4. **Write the test to be red.** Run it — confirm it fails before writing the implementation.

5. **Write the implementation.** Make it green.

## The WHY Convention

Every test must answer: *"What breaks in the product if this test fails?"*

```python
class TestTokenValidation:
    def test_expired_token_raises(self):
        """Expired tokens must be rejected.

        If this fails: users with expired sessions bypass auth —
        they can read and modify data they no longer have access to.
        """
        with pytest.raises(TokenExpiredError):
            verify_token(make_expired_token())
```

A test without a WHY is a test nobody can confidently fix or delete.

## Mocking Externals

Unit tests mock all I/O. Use `monkeypatch`, `unittest.mock`, or in-memory fakes.

### Database mock

```python
class FakeRepo:
    def __init__(self):
        self._store = {}
    def get(self, id):
        return self._store.get(id)
    def save(self, entity):
        self._store[entity.id] = entity
        return entity

def test_user_service_creates_user():
    repo = FakeRepo()
    svc  = UserService(repo)
    user = svc.create(email="a@example.com")
    assert repo.get(user.id) is not None
```

### HTTP client mock

```python
def test_notifies_on_signup(monkeypatch):
    """Signup triggers a welcome notification.

    If this fails: new users never receive onboarding messages.
    """
    sent = []
    monkeypatch.setattr("app.notify.send", lambda **kw: sent.append(kw))
    register_user(email="u@example.com")
    assert len(sent) == 1
```

### Env var defaults (for modules that read env at import)

```python
import os
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@127.0.0.1/test")
os.environ.setdefault("SECRET_KEY", "unit-test-secret")

# import app modules after setting defaults
from app.auth import verify_token
```

## Test Class Structure

```python
class TestFeatureName:
    """One class per behavior area."""

    def test_happy_path(self):
        """Normal input produces expected output.

        If this fails: the core use case is broken.
        """

    def test_edge_case(self):
        """Edge case input is handled gracefully.

        If this fails: [specific consequence].
        """

    def test_error_path(self):
        """Invalid input raises the right error.

        If this fails: errors are swallowed or the wrong error type is raised,
        making debugging harder and error handling in callers incorrect.
        """

    def test_unknown_input_does_not_crash(self):
        """Unknown/future input must not raise unhandled exceptions.

        If this fails: adding a new value to an enum or event type in one
        place breaks all consumers until every handler is updated.
        """
```
