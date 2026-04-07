# Aureon API Module Architecture

## Overview

The API Module is the **entry point** of Aureon. It exposes the system's capabilities as RESTful endpoints, handles HTTP requests, validates input, orchestrates backend modules, and returns responses. It is a **thin layer** — no business logic resides here. All business logic is delegated to the Backend modules (Port/Adapter layer).

---

## Location

```
Aureon/
├── API/                          # FastAPI application
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration (CORS, rate limits, JWT)
│   ├── dependencies.py           # Dependency injection container
│   ├── middleware/               # Request/response processing
│   │   ├── auth.py               # JWT authentication
│   │   ├── logging.py            # Request logging
│   │   └── rate_limit.py         # Rate limiting
│   ├── routes/                   # Endpoint definitions
│   │   ├── auth.py               # Login, logout, refresh
│   │   ├── users.py              # User management
│   │   ├── tenants.py            # Tenant management
│   │   ├── accounts.py           # Chart of accounts
│   │   ├── journals.py           # Journal entries
│   │   ├── loans.py              # Loan lifecycle
│   │   ├── payments.py           # Payment execution
│   │   ├── treasury.py           # Treasury operations
│   │   ├── reports.py            # Financial reports
│   │   └── audit.py              # Audit trail
│   ├── schemas/                  # API-specific request/response models
│   │   ├── auth.py               # LoginRequest, LoginResponse
│   │   └── common.py             # Pagination, ErrorResponse
│   └── utils/                    # Helpers
│       ├── pagination.py         # Pagination utilities
│       └── responses.py          # Standard response formatters
│
├── backend/                      # Business logic (Port/Adapter)
├── Middleware/                   # Data providers
├── schemas/                      # Domain schemas
└── database/                     # Models
```

---

## Responsibilities

### API Layer Does

| Responsibility | Description |
|----------------|-------------|
| **HTTP Handling** | Receive requests, parse bodies, return responses |
| **Authentication** | Validate JWT tokens, extract user context |
| **Authorization** | Check user permissions against endpoint requirements |
| **Input Validation** | Validate request bodies against Pydantic schemas |
| **Orchestration** | Call backend adapters in correct sequence |
| **Error Handling** | Catch exceptions, map to HTTP status codes |
| **Response Formatting** | Standardize JSON responses |
| **Pagination** | Handle limit/offset for list endpoints |
| **Rate Limiting** | Prevent abuse |
| **CORS** | Allow frontend access |
| **OpenAPI** | Auto-generate API documentation |

### API Layer Does NOT Do

| Task | Where It Lives |
|------|----------------|
| Business logic | `backend/` (Port/Adapter) |
| Database operations | `Middleware/DataProvider/` |
| Domain validation | `schemas/` (domain schemas) |
| Database models | `database/` |

---

## Key Components

### 1. Dependency Injection Container

The container is the **heart of the API layer**. It instantiates all backend adapters once per request and wires them together.

**Purpose:**
- Creates a single instance of all providers and adapters
- Injects dependencies (e.g., LoanAdapter needs TreasuryAdapter, PaymentAdapter, AccountingAdapter)
- Makes adapters available to route handlers

**How it works:**
- One container created per HTTP request
- Container holds: database session, current user, current tenant
- All providers initialized with the session
- All adapters initialized with their required providers/other adapters

**Why this pattern:**
- Enables testing (mock containers)
- Ensures each request gets fresh database session
- Makes dependencies explicit and traceable

---

### 2. Authentication Middleware

Runs before every request to protected endpoints.

**Flow:**
1. Extract JWT from `Authorization: Bearer <token>` header
2. Verify token signature and expiration
3. Decode payload (user_id, tenant_id, roles)
4. Attach user and tenant to `request.state`
5. If token invalid → return 401 Unauthorized

**Public routes** (no auth required):
- `/health` — health check
- `/docs` — OpenAPI docs
- `/auth/login` — login endpoint
- `/auth/refresh` — token refresh

---

### 3. Route Handlers

Each route file contains endpoints for a specific domain.

**Structure:**
```
routes/loans.py
├── POST /loans              → Create loan application
├── GET /loans/{id}          → Get loan details
├── GET /loans               → List loans (paginated)
├── POST /loans/{id}/approve → Approve loan
├── POST /loans/{id}/disburse → Disburse loan (orchestrates 5+ modules)
├── POST /loans/{id}/repay   → Process repayment
└── POST /loans/{id}/write-off → Write off loan
```

**Handler pattern:**
```
1. Validate request body (Pydantic schema)
2. Extract user/tenant from request.state
3. Call appropriate backend adapter(s)
4. Catch known exceptions → map to HTTP errors
5. Return formatted response
```

---

### 4. Response Format

All endpoints return standardized JSON.

**Success response:**
```json
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "limit": 20, "total": 100 },
  "links": { "self": "...", "next": "..." }
}
```

**Error response:**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_LIQUIDITY",
    "message": "Insufficient funds for disbursement",
    "details": { "required": 5000, "available": 3200 },
    "request_id": "req_abc123"
  }
}
```

**HTTP status codes:**
| Code | Use |
|------|-----|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Unauthorized |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 422 | Business rule violation |
| 500 | Internal server error |

---

### 5. Configuration

Environment variables control API behavior.

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET_KEY` | Token signing key |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (15 min) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (7 days) |
| `CORS_ORIGINS` | Allowed frontend origins |
| `RATE_LIMIT_REQUESTS` | Max requests per minute (100) |
| `LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR |

---

## Data Flow

```
HTTP Request
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Middleware Chain                                            │
│    - CORS → Logging → Rate Limit → Auth (JWT validation)      │
│    - User & tenant attached to request.state                   │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Route Handler                                                │
│    - Parse request body (Pydantic validation)                  │
│    - Extract user/tenant from request.state                    │
│    - Call get_container() → returns Container with all adapters│
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Backend Adapter Orchestration                                │
│    Example: LoanAdapter.disburse()                             │
│    ├── LoanProvider.get_loan()                                 │
│    ├── TreasuryAdapter.check_liquidity()                       │
│    ├── TreasuryAdapter.reserve_funds()                         │
│    ├── PaymentAdapter.execute_outbound()                       │
│    ├── AccountingAdapter.create_journal()                      │
│    ├── LoanProvider.update_status()                            │
│    └── AuditAdapter.log()                                      │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Response                                                     │
│    - Format as standard JSON                                    │
│    - Apply pagination if needed                                 │
│    - Return HTTP response                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Orchestration Examples

### Simple Endpoint: `GET /loans/{id}`

**Modules involved:** Loans only

```
Request → LoanAdapter.get_loan() → LoanProvider → Response
```

### Complex Endpoint: `POST /loans/{id}/disburse`

**Modules involved:** 5 modules orchestrated

| Step | Module | Action |
|------|--------|--------|
| 1 | Loans | Verify loan is approved |
| 2 | Treasury | Check sufficient liquidity |
| 3 | Treasury | Reserve funds |
| 4 | Payments | Create outbound payment |
| 5 | Payments | Execute via provider (Internal/MTN/Bank) |
| 6 | Accounting | Create journal entry (Dr: Loans Receivable, Cr: Bank) |
| 7 | Loans | Update status to ACTIVE |
| 8 | Loans | Generate repayment schedule |
| 9 | Audit | Log all actions |

If any step fails → rollback previous steps (database transaction)

---

## Error Handling Strategy

| Exception Type | HTTP Status | Example |
|----------------|-------------|---------|
| `ValidationError` | 400 | Invalid amount, missing field |
| `AuthenticationError` | 401 | Invalid token |
| `PermissionError` | 403 | User lacks required role |
| `NotFoundError` | 404 | Loan ID doesn't exist |
| `BusinessRuleError` | 422 | Insufficient liquidity |
| `ProviderError` | 502 | MTN API down |
| `SystemError` | 500 | Database connection lost |

---

## Security

| Layer | Mechanism |
|-------|-----------|
| **Transport** | HTTPS only (TLS 1.3) |
| **Authentication** | JWT with 15-min expiry |
| **Session** | Refresh token (7 days) |
| **Authorization** | Role-based access control |
| **Rate Limiting** | 100 requests/minute per user |
| **CORS** | Whitelisted origins only |
| **Input** | Pydantic validation |
| **Output** | No sensitive data leaked in errors |

---

## File Structure Summary

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, middleware registration, router includes |
| `config.py` | Environment variables, settings |
| `dependencies.py` | DI container (wires all adapters) |
| `middleware/auth.py` | JWT validation, user extraction |
| `middleware/logging.py` | Request/response logging |
| `middleware/rate_limit.py` | Rate limiting |
| `routes/*.py` | Endpoint definitions per domain |
| `schemas/*.py` | Request/response models |
| `utils/*.py` | Pagination, response formatters |

---

## Development Workflow

### Adding a New Endpoint

1. Identify which backend adapter(s) to call
2. Create request/response schemas in `API/schemas/`
3. Add route handler in appropriate `routes/` file
4. Call container.`adapter.method()` with validated data
5. Map exceptions to HTTP errors
6. Return formatted response

### Testing Strategy

| Level | Scope |
|-------|-------|
| **Unit** | Individual route handlers (mocked container) |
| **Integration** | End-to-end with test database |
| **Contract** | OpenAPI schema validation |

---

## Next Steps

After reviewing this document, we will:

1. **Create directory structure** — `API/` with subfolders
2. **Build dependencies.py** — the container that wires all modules
3. **Build auth middleware** — JWT validation
4. **Build auth routes** — login, logout, refresh
5. **Build loan routes** — starting with simple GET endpoints
6. **Build complex orchestration** — loan disbursement (5 modules)