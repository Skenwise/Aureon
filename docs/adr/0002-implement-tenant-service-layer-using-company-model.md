# 2. Implement Tenant Service Layer Using Company Model

Date: 2026-01-25

## Status

Accepted

## Context

Following the decision to prioritize tenants and identity modules before accounting, and to use the existing Company model as the tenant entity, we need to implement the tenant management functionality. The Company model already exists in the database schema and serves as the foundation for multi-tenancy.

## Decision

We will implement a service layer for tenant management in `backend/tenants/tenant.py` that:

- Defines separate Pydantic schemas for create, update, and read operations (TenantCreate, TenantUpdate, TenantRead)
- Creates a TenantService class that encapsulates CRUD operations on the Company model
- Uses dependency injection with a database session
- Follows SQLModel conventions with proper type hinting and docstrings
- Includes basic validation (e.g., unique code checking)
- Separates read schema from the internal model for API safety

The service will provide:
- create_tenant: Create new tenant with validation
- get_tenant_by_id: Retrieve by UUID
- get_tenant_by_code: Retrieve by unique code
- update_tenant: Partial updates with validation
- list_tenants: List all tenants

## Consequences

- Provides a clean abstraction layer for tenant operations
- Maintains separation between internal models and API schemas
- Enables easy testing and mocking of tenant operations
- Sets precedent for other service layers in the application
- Requires careful handling of the Company model's multi-tenant field (company_id) which may be null for tenant records themselves</content>
<parameter name="filePath">/home/skenwise/dbs/Desktop/Project/Aureon/docs/adr/0002-implement-tenant-service-layer-using-company-model.md