# Insecure Defaults: Examples and Counter-Examples

## Fallback Secrets

### VULNERABLE
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
# App runs with known secret if SECRET_KEY missing → attacker forges tokens
```

### SECURE
```python
SECRET_KEY = os.environ['SECRET_KEY']  # Raises KeyError if missing → fail-secure
```

## Default Credentials

### VULNERABLE
```python
def bootstrap_admin():
    admin = User(username='admin', password=hash_password('admin123'), role='admin')
    # Default admin with known credentials
```

### SECURE
```python
def bootstrap_admin():
    username = os.environ['ADMIN_USERNAME']  # Crash if not configured
    password = os.environ['ADMIN_PASSWORD']
```

## Fail-Open Security

### VULNERABLE
```python
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'false').lower() == 'true'
# Default = no authentication!

CORS_ORIGIN = process.env.ALLOWED_ORIGINS || '*'
# Default = allow all origins!

DEBUG = os.getenv('DEBUG', 'true').lower() != 'false'
# Default = debug mode on!
```

### SECURE
```python
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'true').lower() == 'true'  # Default: true
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'  # Default: false
```

## Weak Crypto

### VULNERABLE
```python
hashlib.md5(password.encode()).hexdigest()  # MD5 broken for passwords
crypto.createHmac('sha1', secret)  # SHA1 collisions exist
```

### SECURE
```python
bcrypt.hashpw(password.encode(), bcrypt.gensalt())  # Modern password hashing
```

## Debug Features

### VULNERABLE
```python
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({'error': str(error), 'traceback': traceback.format_exc()}), 500
    # Leaks internal paths, library versions
```

### SECURE
```python
@app.errorhandler(Exception)
def handle_error(error):
    logger.exception('Request failed', exc_info=error)  # Logs full trace
    return jsonify({'error': 'Internal server error'}), 500  # Generic to user
```
