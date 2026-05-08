---
name: static
description: Static harness layer. Use when a coding agent needs to choose, write, or run structural invariant tests — checks that require no running services, no app imports, and no network. Covers forbidden patterns, file existence, AST-level structure, dependency policy, and documentation invariants.
---

# Static

Use this skill for the static layer of the full testing environment:

```
full testing environment = static + unit + browser
```

## Scope

Static tests verify project facts without running the product:

- forbidden patterns (code that must never appear)
- required patterns (code that must appear in specific files)
- file existence (required files and directories)
- AST-level structure (constant coverage, import policy)
- dependency pinning and build config
- documentation invariants (required sections, placeholder validity)
- tracking directory structure

Do not import app modules in this layer. Use only filesystem reads, `ast.parse()`, and `re` text analysis.

## Execution

```bash
./strata/testing.sh static
python3 -m pytest strata/static.py -q --tb=short   # direct, for debugging
```

## When To Add Static Coverage

Add or update `strata/static.py` when a change depends on:

- a required file or directory always being present
- a pattern that must never appear in source (silent exceptions, hardcoded credentials, banned imports)
- a set of constants that must all be handled somewhere (event types, command names, status codes)
- a config file or template containing required content
- a dependency staying pinned or below a version
- a structural convention that would be easy to break silently

Static must fail *before* product code is written when the invariant is visible from source text or filesystem structure.

## How To Add A Check

1. **Identify the invariant.** State it in one sentence: "X must always be true about the structure of this project."

2. **Choose the pattern:**

   | What you need to verify | Pattern |
   |------------------------|---------|
   | A file exists | `assert path.exists()` |
   | A string never appears | `re.compile(pattern)` + loop over `ROOT.glob(...)` |
   | A string always appears in a file | `assert "token" in path.read_text()` |
   | All items in a set are handled | `_string_constants_in_tuple()` + set diff |
   | A template has required placeholders | `assert "{VAR}" in template_text` |

3. **Write the failing test first.** Run `./strata/testing.sh static` — it must be red before the invariant is enforced.

4. **Write the fix.** Enforce the invariant in the product code.

5. **Run again.** Static must go green.

## The WHY Convention

Every test function must have a docstring that answers:
*"What breaks in the product if this test fails?"*

```python
def test_no_silent_exceptions():
    """Silent exception handlers must not exist in production source.

    If this fails: crashes are swallowed silently — bugs become invisible,
    production incidents have no log evidence, debugging takes hours longer.
    """
```

This is not optional. A test without a WHY is a test nobody knows whether to fix or delete.

## Common Patterns

### Forbidden pattern across all source files

```python
PATTERN = re.compile(r"except\s+Exception\s*:\s*\n\s*pass")

def test_no_silent_exceptions():
    for path in ROOT.glob("**/*.py"):
        if "strata/" in str(path) or ".venv/" in str(path):
            continue
        assert not PATTERN.search(path.read_text()), \
            f"Silent exception in {path}"
```

### Required pattern in specific files

```python
def test_routes_register_auth():
    for path in ROOT.glob("src/routes/*.js"):
        assert "authMiddleware" in path.read_text(), \
            f"{path.name} must apply authMiddleware"
```

### Constant coverage via AST

```python
def _constants(path, var_name):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == var_name for t in node.targets):
                if isinstance(node.value, (ast.Tuple, ast.List)):
                    return {e.value for e in node.value.elts
                            if isinstance(e, ast.Constant)}
    return set()

def test_all_commands_registered():
    defined  = _constants(SRC / "commands.py", "ALL_COMMANDS")
    handler  = (SRC / "dispatcher.py").read_text()
    missing  = {c for c in defined if c not in handler}
    assert not missing, f"Commands not handled: {missing}"
```

### Template placeholder integrity

```python
def test_config_template_has_placeholder():
    template = (ROOT / "config/app.template.yaml").read_text()
    assert "{DATABASE_URL}" in template, \
        "app.template.yaml must contain {DATABASE_URL} placeholder"
```
