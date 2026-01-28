# Auth.py – Technical Deep Dive

## Overview
This document explains the technical decisions and teaching points behind the `AuthenticationAdapter` implementation.

---

## Architecture Pattern

### Port–Adapter (Hexagonal) Pattern

```

API Layer
↓
AuthenticationPort (Contract)
↓
AuthenticationAdapter (Implementation)
↓
UserProvider (Data Access)

````

### Why this matters
- The **Port** defines *what* authentication does  
- The **Adapter** defines *how* it does it  
- The API layer only knows about the **Port**  
- Infrastructure can be swapped without touching the Port  

---

## Key Components

---

## 1. Password Hashing with bcrypt

### Why bcrypt and not SHA-256 or MD5?

```python
@staticmethod
def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )
````

### Technical reasons

* **Slow by design** – configurable work factor
* **Prevents brute force** – expensive even on GPUs
* **Built-in salt** – unique salt per hash
* **Future-proof** – work factor can be increased as hardware improves

### Alternatives and why we didn’t use them

* ❌ **SHA-256** – too fast, no salt, designed for checksums
* ❌ **MD5** – broken, collision attacks exist
* ✅ **bcrypt** – industry standard
* ✅ **Alternatives** – Argon2, scrypt (also acceptable)

### Constant-time comparison

* Normal string comparison exits on first mismatch
* Attackers can measure response time
* `bcrypt.checkpw` performs constant-time comparison internally

---

## 2. JWT Token Generation

### What is a JWT?

A **JWT (JSON Web Token)** is a self-contained token with three parts:

```
Header.Payload.Signature
```

### Example JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJ1c2VyX2lkIjoiMTIzIiwidXNlcm5hbWUiOiJqb2huIn0
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Decoded

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "user_id": "123",
  "username": "john",
  "iat": 1706380800,
  "exp": 1706467200
}
```

### Why JWT?

* ✅ Stateless – no server-side sessions
* ✅ Self-contained – all claims inside token
* ✅ Scalable – works across multiple servers
* ✅ Standard – supported everywhere

### JWT payload rules

```python
payload = {
    'user_id': user_id,     # ✅ Safe
    'username': username,   # ✅ Safe
    'iat': now,
    'exp': expiry
}
```

❌ Never include:

* Passwords
* Credit card numbers
* SSNs
* API keys

> JWTs are **encoded**, not encrypted.

---

## 3. Token Expiration Strategy

```python
token_expiry_hours: int = 24
```

### Security vs UX Tradeoff

| Expiry   | Security      | UX                  |
| -------- | ------------- | ------------------- |
| 5 min    | ✅ Very secure | ❌ Constant re-login |
| 1 hour   | ✅ Secure      | ⚠️ Mild friction    |
| 24 hours | ⚠️ Moderate   | ✅ Good UX           |
| 7 days   | ❌ Risky       | ✅ Smooth UX         |

### Industry standards

* **Access tokens:** 15–60 minutes
* **Refresh tokens:** 7–30 days

### Best practice

* Short-lived access token
* Long-lived refresh token
* Refresh token stored securely (HttpOnly / secure storage)

---

## 4. Error Translation

```python
except jwt.ExpiredSignatureError:
    raise AuthenticationError("Token has expired")

except jwt.InvalidTokenError as e:
    raise AuthenticationError(f"Invalid token: {str(e)}")
```

### Why translate errors?

❌ Bad (infrastructure leak):

```python
raise jwt.ExpiredSignatureError
```

✅ Good (domain error):

```python
raise AuthenticationError("Token has expired")
```

### Benefits

* API layer doesn’t know JWT exists
* Can swap JWT → OAuth without API changes
* Consistent domain-level error handling

---

## Implementation Flow

---

### Authenticate Flow

1. API calls `auth.authenticate(username, password)`
2. Adapter retrieves user
3. Password verified with bcrypt
4. JWT generated
5. Token returned to API

```python
def authenticate(self, username: str, password: str) -> str:
    user = self.provider.get_user_by_username(username)

    if not user:
        raise AuthenticationError("Invalid username or password")

    if not self._verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid username or password")

    return self._generate_token(user.id, user.username)
```

**Security note:**
Same error message prevents username enumeration.

---

### Verify Token Flow

1. API calls `auth.verify_token(token)`
2. JWT decoded
3. Signature + expiration validated
4. Payload returned

```python
def verify_token(self, token: str) -> Dict[str, str]:
    try:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
```

---

## Dependencies

```bash
pip install bcrypt PyJWT
```

### bcrypt

* Purpose: Password hashing
* Version: 4.0+
* License: Apache 2.0

### PyJWT

* Purpose: JWT encoding/decoding
* Version: 2.8+
* License: MIT

---

## Security Checklist

### ✅ Implemented

* bcrypt password hashing
* Constant-time comparison
* JWT with expiration
* Error translation
* Minimal token payload

### ⚠️ Future

* Refresh tokens
* Token revocation
* MFA
* OAuth2
* Rate limiting

---

## Testing Strategy

### Unit Tests (Adapter)

```python
def test_authenticate_success(): ...
def test_authenticate_wrong_password(): ...
def test_authenticate_user_not_found(): ...
def test_verify_token_success(): ...
def test_verify_token_expired(): ...
def test_verify_token_invalid(): ...
```

### Integration Tests (API)

```python
def test_login_endpoint(): ...
def test_protected_endpoint(): ...
def test_protected_endpoint_no_token(): ...
```

---

## Common Mistakes to Avoid

### ❌ Plaintext passwords

```python
user.password = password
```

✅ Correct:

```python
user.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

---

### ❌ Sensitive JWT payload

```python
payload = {
    'password': user.password,
    'credit_card': user.cc_number
}
```

✅ Correct:

```python
payload = {
    'user_id': user.id,
    'username': user.username
}
```

---

### ❌ Infrastructure error leaks

```python
raise jwt.ExpiredSignatureError
```

✅ Correct:

```python
raise AuthenticationError("Token has expired")
```

---

### ❌ Username enumeration

```python
raise AuthenticationError("User not found")
```

✅ Correct:

```python
raise AuthenticationError("Invalid username or password")
```

---

## Next Steps

* ✅ Implement `role.py`
* ✅ Implement `permission.py`
* ✅ Integrate auth into API
* ✅ Write unit tests
* ✅ Write integration tests

---

## Reflection Questions

* Why bcrypt over SHA-256?
* Encoding vs encryption?
* Why token expiration is a UX tradeoff?
* Purpose of Port–Adapter?
* Why translate JWT errors?

---

## Summary

### Key Takeaways

* Authentication is a **domain concern**
* Port defines the contract
* Adapter implements behavior
* bcrypt for secure password storage
* JWT for stateless identity
* Clean boundaries via error translation
* Never store sensitive data in JWTs

> **Identity defines truth.
> Authentication proves it temporarily.**

```

---

If you want next:
- same treatment for `authorization.md`
- or an **ADR-style version** of this  
- or trimming it into **teaching slides**

Just say the word.
```
