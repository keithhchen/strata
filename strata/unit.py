"""
Unit tests for pure logic.
No server, no network, no database, no browser.
All external dependencies are mocked or replaced with in-memory fakes.
Target: < 5s total.

HOW TO USE THIS FILE
====================
Copy it into your project's strata/ directory, then replace the examples
with tests for your project's actual logic.

Run:
  python3 -m pytest strata/unit.py -q --tb=short
  ./strata/testing.sh unit

WHAT BELONGS HERE
=================
  - Pure functions (parsers, validators, formatters, calculators)
  - State machines and reducers
  - Auth/permission logic that doesn't require a real DB
  - Event/message mapping and dispatch
  - Error-path behavior that can be triggered in isolation
  - Path resolution and containment checks

WHAT DOES NOT BELONG HERE
==========================
  - Anything that requires a running server or database
  - Anything that makes HTTP or WebSocket calls
  - Anything that renders a browser UI
  - Anything that writes to the real filesystem

THE WHY CONVENTION
==================
Every test docstring must answer: "What breaks in the product if this test fails?"
Example:
    def test_expired_token_raises():
        \"\"\"Expired tokens must be rejected.

        If this fails: users with expired sessions bypass auth —
        they can read and modify data they no longer have access to.
        \"\"\"

This discipline forces you to understand why the test exists, and helps
future contributors know whether a failing test is a blocker or a flap.
"""

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Pure function test class
#
# Group tests by behavior, not by function name.
# One class = one behavior area.
# ─────────────────────────────────────────────────────────────────────────────

# class TestJwtValidation:
#     def test_expired_token_raises(self):
#         """Expired tokens must be rejected.
#
#         If this fails: users with expired sessions bypass auth —
#         they can read and modify data they no longer have access to.
#         """
#         with pytest.raises(TokenExpiredError):
#             verify_jwt(make_expired_token())
#
#     def test_valid_token_returns_payload(self):
#         """Valid tokens return the decoded payload.
#
#         If this fails: every authenticated request fails — app is unusable.
#         """
#         payload = verify_jwt(make_valid_token(user_id="u-1"))
#         assert payload["user_id"] == "u-1"
#
#     def test_tampered_token_raises(self):
#         """Tokens with invalid signatures must be rejected.
#
#         If this fails: an attacker can forge tokens and impersonate any user.
#         """
#         with pytest.raises(InvalidSignatureError):
#             verify_jwt(make_tampered_token())


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Parser test class
#
# Parsers should be tested with all edge cases inline.
# Use small, self-contained input fixtures.
# ─────────────────────────────────────────────────────────────────────────────

# class TestPaginationParser:
#     def test_defaults_when_missing(self):
#         """Missing pagination params use safe defaults.
#
#         If this fails: unpaginated endpoints return unbounded result sets
#         that can exhaust DB memory under load.
#         """
#         result = parse_pagination({})
#         assert result.limit == 20
#         assert result.offset == 0
#
#     def test_limit_clamped_to_max(self):
#         """limit > MAX_PAGE_SIZE is clamped, not rejected.
#
#         If this fails: clients can request arbitrarily large pages,
#         bypassing the intent of pagination.
#         """
#         result = parse_pagination({"limit": "9999"})
#         assert result.limit <= MAX_PAGE_SIZE


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Path containment test class
#
# Use this for any code that resolves user-supplied paths.
# This is a security invariant: traversal must be rejected.
# ─────────────────────────────────────────────────────────────────────────────

# class TestPathContainment:
#     def test_relative_path_resolves_inside_root(self, tmp_path):
#         """Normal relative paths resolve inside the workspace root.
#
#         If this fails: legitimate file requests are rejected — users
#         cannot access their own files.
#         """
#         target = tmp_path / "uploads" / "logo.png"
#         target.parent.mkdir(parents=True)
#         target.write_bytes(b"")
#         resolved = resolve_safe_path(tmp_path, "uploads/logo.png")
#         assert resolved == target.resolve()
#
#     def test_parent_traversal_raises(self, tmp_path):
#         """../  traversal must be rejected with ValueError.
#
#         If this fails: any authenticated user can read arbitrary files
#         from the server — including other users' data and system files.
#         """
#         with pytest.raises(ValueError):
#             resolve_safe_path(tmp_path, "../etc/passwd")
#
#     def test_absolute_path_raises(self, tmp_path):
#         """/absolute paths must be rejected with ValueError.
#
#         If this fails: users can escape the workspace root entirely
#         and access any path on the filesystem.
#         """
#         with pytest.raises(ValueError):
#             resolve_safe_path(tmp_path, "/etc/passwd")
#
#     def test_symlink_escape_raises(self, tmp_path):
#         """Symlinks pointing outside the workspace root must be rejected.
#
#         If this fails: an attacker can create a symlink inside the workspace
#         that points to a sensitive file outside it.
#         """
#         outside = tmp_path / "outside"
#         outside.mkdir()
#         (tmp_path / "link").symlink_to(outside)
#         with pytest.raises(ValueError):
#             resolve_safe_path(tmp_path, "link/secret.txt")


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: External dependency mock
#
# For logic that calls an external service, mock the call and test the
# behavior around it — not the service itself.
# ─────────────────────────────────────────────────────────────────────────────

# class TestEmailNotification:
#     def test_sends_email_on_signup(self, monkeypatch):
#         """New user signup triggers a welcome email.
#
#         If this fails: users sign up and never receive confirmation —
#         they cannot verify their email address.
#         """
#         sent = []
#         monkeypatch.setattr("app.mailer.send", lambda **kw: sent.append(kw))
#
#         register_user(email="user@example.com", password="s3cret")
#
#         assert len(sent) == 1
#         assert sent[0]["to"] == "user@example.com"
#         assert "welcome" in sent[0]["subject"].lower()
#
#     def test_mailer_failure_does_not_rollback_user(self, monkeypatch):
#         """Email delivery failure must not prevent user creation.
#
#         If this fails: a flaky email provider causes user registrations to
#         fail — new users are lost even though the core action succeeded.
#         """
#         monkeypatch.setattr("app.mailer.send", lambda **kw: (_ for _ in ()).throw(TimeoutError()))
#         user = register_user(email="user2@example.com", password="s3cret")
#         assert user.id is not None


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN: Unknown input does not crash
#
# Future-proofing: new message types, event types, or enum values
# must not raise unhandled exceptions in dispatch/switch code.
# ─────────────────────────────────────────────────────────────────────────────

# class TestDispatchRobustness:
#     def test_unknown_event_type_does_not_raise(self):
#         """Unknown event types must be ignored, not crash the handler.
#
#         If this fails: adding a new event type to the producer breaks
#         the consumer — the system crashes until both sides are deployed.
#         """
#         dispatcher = EventDispatcher()
#         try:
#             dispatcher.handle({"type": "future_event_type_v99", "data": {}})
#         except Exception as e:
#             pytest.fail(f"Unknown event type raised: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# STARTER: A real test to verify the harness itself works
# Delete this once you have real tests.
# ─────────────────────────────────────────────────────────────────────────────

def test_harness_unit_layer_is_wired():
    """Placeholder: confirms the unit harness runs.

    Replace this with your first real unit test.
    """
    assert True
