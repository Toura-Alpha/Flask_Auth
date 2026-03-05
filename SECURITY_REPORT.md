# Flask Authentication Security Report

## Executive Summary

This report provides a comprehensive security analysis of the Flask authentication system. The application implements user registration, login (both credentials-based and Google OAuth), and session management. Several security issues were identified and are documented below.

---

## Issues Fixed

### 1. Database Schema Mismatch (RESOLVED)

- **Severity:** High
- **Issue:** The SQLite database had a `NOT NULL` constraint on `password_hash` column, but the SQLAlchemy model allowed `nullable=True`. This caused `IntegrityError` when creating users via Google OAuth (who don't have passwords).
- **Resolution:** Recreated the `user` table to remove the constraint.

---

## Critical Security Issues

### 2. Hardcoded Secrets

- **Severity:** Critical
- **Location:** `app.py` line 9, `api_key.py`

**Current Code (app.py):**

```python
app.config['SECRET_KEY'] = 'your_secret_key'
```

**Current Code (api_key.py):**

```python
CLIENT_ID="178285835772-80sinbmf3eqtvdrs9b1qeo4nf1g4vrdc.apps.googleusercontent.com"
CLIENT_SECRET="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"
```

**Risks:**

- Secret keys exposed in source code
- If code is committed to version control, secrets are leaked
- Google OAuth credentials can be stolen and misused

**Recommendation:**

```python
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))

# In api_key.py or use environment variables:
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
```

---

### 3. Missing CSRF Protection

- **Severity:** High
- **Location:** All forms in `templates/index.html`

**Issue:** Forms do not use CSRF tokens, making them vulnerable to Cross-Site Request Forgery attacks.

**Recommendation:**

```python
# In app.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

# Enable CSRF protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('WTF_CSRF_SECRET_KEY', os.urandom(32))

# In templates, use:
<form method="POST">
    {{ form.hidden_tag() }}
    ...
</form>
```

Install: `pip install flask-wtf`

---

### 4. No Password Strength Validation

- **Severity:** Medium
- **Location:** `app.py` - `register()` function

**Issue:** No minimum password length or complexity requirements.

**Current Code:**

```python
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    # No validation!
```

**Recommendation:**

```python
import re

def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain letters"
    if not re.search(r"[0-9]", password):
        return "Password must contain numbers"
    return None

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    error = validate_password(password)
    if error:
        return render_template('index.html', error=error)
```

---

## Medium Security Issues

### 5. Relative Database Path

- **Severity:** Medium
- **Location:** `app.py` line 11

**Current:**

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
```

**Issue:** Relative paths can be ambiguous and cause issues when running from different directories.

**Recommendation:**

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "users.db")}'
```

---

### 6. Session Security

- **Severity:** Medium
- **Location:** `app.py`

**Current:** Default Flask session cookies (not secure by default).

**Recommendation:**

```python
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
```

---

### 7. OAuth Token Storage

- **Severity:** Low
- **Location:** `app.py` - `authorize()` function

**Current:**

```python
session['oauth_token'] = token
```

**Issue:** OAuth tokens are stored in the session cookie. While not inherently insecure, these should be stored server-side if they need to be used for API calls.

**Note:** If the token is not being used for anything, it shouldn't be stored.

---

## Good Security Practices Observed

### ✓ Password Hashing

The application uses Werkzeug's `generate_password_hash()` which uses PBKDF2-SHA256 by default - this is secure.

```python
def set_password(self, password):
    self.password_hash = generate_password_hash(password)
```

### ✓ SQL Injection Protection

The application uses SQLAlchemy ORM, which automatically handles SQL injection protection.

### ✓ Input Validation

Basic input validation is present (checking for empty username/password).

---

## Summary of Recommendations

| Priority | Issue                   | Fix                          |
| -------- | ----------------------- | ---------------------------- |
| Critical | Hardcoded secrets       | Use environment variables    |
| High     | Missing CSRF protection | Use Flask-WTF                |
| Medium   | No password validation  | Add length/complexity checks |
| Medium   | Session cookie security | Add cookie flags             |
| Low      | OAuth token handling    | Review if needed             |

---

## Implementation Checklist

- [ ] Move secrets to environment variables
- [ ] Install and configure Flask-WTF for CSRF protection
- [ ] Add password strength validation
- [ ] Configure secure session cookies
- [ ] Review OAuth token storage needs
- [ ] Add rate limiting for login attempts (prevent brute force)
- [ ] Add account lockout after failed attempts
- [ ] Implement proper error messages (don't reveal if username exists)

---

_Report generated for Flask_Auth project_
