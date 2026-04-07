# Aureon Layer Architecture Protocol

## The Four Stages of Sterile Corridor Implementation

**Document Version:** 1.0  
**Status:** Active  
**Applies To:** All layers (Provider, Adapter, API, Reporting)

---

## Overview

The Aureon Layer Architecture Protocol defines a **four-stage process** for building and validating each layer of the system. Every layer—from Database Provider to API endpoint—must pass through these four stages before being considered complete.

The core principle is the **Sterile Corridor**: no raw data ever crosses a layer boundary. Every input and output is validated by a strict Pydantic schema, and errors are translated at each boundary.

---

## Stage 1: The Interface Contract (Schemas)

### Goal
Define the strict Pydantic schemas that act as gatekeepers for the layer.

### Why Before Code
Defining the data shape before writing logic forces us to think about what the layer above actually needs. It prevents "just add one more field" entropy.

### What We Produce
- Input schema (e.g., `CurrencyProviderInput`)
- Output schema (e.g., `CurrencyProviderOutput`)
- Error types (if layer-specific)

### Validation Rules
| Rule | Description |
|------|-------------|
| No raw DB models | Schema cannot import from `database.model` |
| No layer leakage | Schema cannot import from higher layers |
| Full typing | All fields have type hints |
| Explicit optional | `Optional[T]` for nullable fields |

### File Location
```
schemas/provider/currency.py          # Provider boundaries
schemas/adapter/currency.py           # Adapter boundaries
schemas/api/currency.py               # API boundaries
schemas/domain/                       # Shared domain schemas
```

### Example
```python
# schemas/provider/currency.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class CurrencyProviderInput(BaseModel):
    """Input schema for CurrencyProvider operations."""
    code: str = Field(..., min_length=3, max_length=3)
    name: str = Field(..., max_length=50)
    decimals: int = Field(default=2, ge=0, le=4)

class CurrencyProviderOutput(BaseModel):
    """Output schema for CurrencyProvider operations."""
    id: UUID
    code: str
    name: str
    decimals: int
    created_at: datetime
    updated_at: datetime
```

---

## Stage 2: The Implementation (The Code)

### Goal
Implement the layer to enforce the Sterile Corridor using the schemas defined in Stage 1.

### What We Produce
- The layer implementation (e.g., `CurrencyProvider`)
- Error translation (SQLAlchemy → Domain errors)
- Context propagation (tenant isolation via `contextvars`)

### Core Rules

| Rule | Description |
|------|-------------|
| **Input validation** | All inputs pass through Stage 1 schema |
| **Output validation** | All outputs pass through Stage 1 schema |
| **Error translation** | No raw SQLAlchemy/Provider errors escape |
| **Tenant isolation** | `company_id` from `contextvars`, never as parameter |
| **No layer skipping** | Cannot import from higher layers |

### Error Translation Pattern
```python
try:
    result = self.session.execute(stmt)
except IntegrityError as e:
    if "duplicate" in str(e):
        raise DomainError("Record already exists")
    raise DomainError(f"Database error: {str(e)}")
```

### Tenant Isolation Pattern
```python
# Use contextvars for tenant
from contextvars import ContextVar

current_tenant: ContextVar[UUID] = ContextVar("current_tenant")

class Provider:
    def get(self, id: UUID):
        tenant = current_tenant.get()
        return self.session.execute(
            select(Model).where(
                Model.id == id,
                Model.tenant_id == tenant
            )
        )
```

---

## Stage 3: The Quality Gate (Black & Ruff)

### Goal
Automatically enforce code quality and architectural rules.

### Commands
```bash
# Format code
black .

# Lint and fix
ruff check . --fix

# Run both
black . && ruff check . --fix
```

### What Black Enforces

| Rule | Description |
|------|-------------|
| Line length | 88 characters |
| Quotes | Double quotes for strings |
| Spacing | Consistent indentation and spacing |

### What Ruff Enforces (Architectural Rules)

| Rule | Purpose |
|------|---------|
| `BAN_IMPORT` | Prevent imports from higher layers |
| `BAN_DIRECT_DB` | Prevent direct SQLAlchemy in Adapters |
| `BAN_RAW_ERROR` | Prevent raising raw SQLAlchemy errors |
| `REQUIRE_SCHEMA` | Require schema validation on public methods |

### Validation Criteria
- ✅ Zero Ruff errors
- ✅ Zero Black changes after first pass
- ✅ No manual intervention required

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        entry: black
        language: system
        types: [python]
      - id: ruff
        name: ruff
        entry: ruff check --fix
        language: system
        types: [python]
```

---

## Stage 4: The Proof (Isolated Testing)

### Goal
Prove the layer works correctly in isolation with a sterile test environment.

### Test Harness
```python
# tests/conftest.py
@pytest.fixture(scope="function", name="db_session")
def db_session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        SQLModel.metadata.drop_all(engine)
        engine.dispose()
```

### What We Test

| Test Type | Purpose | Example |
|-----------|---------|---------|
| **Happy Path** | Normal operation works | `test_create_currency` |
| **Error Translation** | DB errors become domain errors | `test_duplicate_raises_domain_error` |
| **Tenant Isolation** | Data doesn't leak across tenants | `test_cross_tenant_isolation` |
| **Required Fields** | Missing required fields rejected | `test_missing_code_raises_error` |
| **Unique Constraints** | Duplicate data rejected | `test_duplicate_raises_error` |

### Test File Structure
```
tests/
├── conftest.py
├── providers/
│   └── test_currency_provider.py
├── adapters/
│   └── test_currency_adapter.py
└── api/
    └── test_currency_api.py
```

### Example Test
```python
# tests/providers/test_currency_provider.py
def test_create_currency(db_session):
    provider = CurrencyProvider(db_session)
    
    input_data = CurrencyProviderInput(
        code="USD",
        name="US Dollar",
        decimals=2
    )
    
    result = provider.create(input_data)
    
    assert result.code == "USD"
    assert result.name == "US Dollar"
    assert result.id is not None
```

### Validation Criteria
- ✅ All tests pass (`pytest` green)
- ✅ No test leaks state (isolation proven)
- ✅ 100% coverage of public methods
- ✅ Error paths tested

---

## The Four-Stage Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 1: SCHEMAS                                  │
│                                                                             │
│  Write Pydantic schemas for input/output boundaries                        │
│                                                                             │
│  Validation: No DB models imported, full typing, explicit optionals        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 2: CODE                                     │
│                                                                             │
│  Implement layer with Sterile Corridor:                                     │
│  - Inputs validated by Stage 1 schemas                                      │
│  - Outputs validated by Stage 1 schemas                                     │
│  - Errors translated to domain errors                                       │
│  - Tenant from contextvars                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 3: QUALITY                                  │
│                                                                             │
│  Run: black . && ruff check . --fix                                         │
│                                                                             │
│  Validation: Zero Ruff errors, zero Black changes                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 4: PROOF                                    │
│                                                                             │
│  Write isolated tests using db_session fixture                              │
│                                                                             │
│  Validation: pytest green, 100% coverage, no state leaks                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                              ✅ LAYER COMPLETE
                          Ready for next layer
```

---

## The Golden Rule

> **If Stage 4 fails, we DO NOT move to the next layer.**
>
> We fix the code, re-run Stage 3, and re-run Stage 4.
>
> **No exceptions.**

---

## Layer Completion Checklist

| Stage | Task | Status |
|-------|------|--------|
| 1 | Schemas written and validated | ☐ |
| 2 | Code implemented with Sterile Corridor | ☐ |
| 3 | Black and Ruff pass with zero errors | ☐ |
| 4 | All tests pass in isolation | ☐ |

---

## Why Four Stages, Not Five?

We removed the intermediate commit stage. Commits happen at natural boundaries (e.g., after completing a full layer or module), not after every Stage 3 pass. This keeps history meaningful and prevents commit noise.

**When to commit:**
- After completing all 4 stages for a logical module
- After fixing a significant bug
- At natural stopping points (end of day, before context switch)

**What we commit:**
- Working, tested, formatted code
- With conventional commit messages
- Not intermediate work-in-progress

---

## Appendix: Quick Reference

| Stage | Name | What | Command/Output |
|-------|------|------|----------------|
| 1 | Schemas | Define boundaries | Write Pydantic schemas |
| 2 | Code | Implement layer | Write code |
| 3 | Quality | Format & lint | `black . && ruff check .` |
| 4 | Proof | Test isolation | `pytest` → green |

---

**Document Owner:** Architecture Team  
**Last Updated:** April 7, 2026  
**Next Review:** After first layer implementation