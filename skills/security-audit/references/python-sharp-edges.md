# Python Sharp Edges

## Mutable Default Arguments

```python
# DANGEROUS: Default is shared across all calls
def append_to(item, target=[]):
    target.append(item)
    return target

append_to(1)  # [1]
append_to(2)  # [1, 2] - same list!
```

**Fix**: Use `None` sentinel:
```python
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

## Eval, Exec, and Code Execution

```python
# DANGEROUS: Arbitrary code execution
eval(user_input)
exec(user_input)

# DANGEROUS: Deserialization
pickle.loads(user_data)       # arbitrary code execution
yaml.load(user_data)          # use safe_load instead
subprocess.Popen(shell=True)  # with user input = RCE
```

## Exception Handling Pitfalls

```python
# DANGEROUS: Bare except catches everything
try:
    risky_operation()
except:  # Catches KeyboardInterrupt, SystemExit
    pass

# DANGEROUS: Silently swallowing security errors
try:
    important_security_check()
except SomeError:
    pass  # Security check failure ignored!
```

## String Formatting Injection

```python
# DANGEROUS: Format string with user data as format spec
template = user_input  # "{0.__class__.__mro__[1].__subclasses__()}"
template.format(some_object)  # Can access arbitrary attributes!
```

**Fix**: Use string concatenation or safe templating (Jinja2 with autoescape).

## Subprocess Shell Injection

```python
# DANGEROUS: shell=True with user input
subprocess.run(f"ls {user_input}", shell=True)
# user_input = "; rm -rf /" → command injection

# SAFE: Use list form without shell
subprocess.run(["ls", user_input])
```

## Numeric Precision

```python
# DANGEROUS: Float comparison
0.1 + 0.2 == 0.3  # False!
# Use math.isclose() or Decimal for financial calculations
```

## Detection Patterns

| Pattern | Risk |
|---------|------|
| `def f(x=[])` or `def f(x={})` | Mutable default argument |
| `eval(`, `exec(`, `compile(` | Code execution |
| `pickle.loads(`, `yaml.load(` | Deserialization RCE |
| `except:` or `except Exception:` | Over-broad exception catching |
| `template.format(obj)` with user template | Format string injection |
| `subprocess.*(..., shell=True)` | Command injection |
| `hashlib.md5` for passwords | Weak crypto |
| `os.open(..., 0o666)` | Permissive file permissions |
