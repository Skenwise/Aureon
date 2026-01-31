# Session 2026-01-28: Identity Module – Permissions and Roles Implementation

Date: 2026-01-28

## Status

Accepted

## Context

Following the completion of **User management**, this session focused on the **Role and Permission subsystem** within the Identity module. The objective was to define **immutable roles**, **permission schemas**, **role-permission mappings**, and their **providers, ports, and adapters**, while preserving **hexagonal architecture principles** and maintaining **high-quality PEP 257-compliant documentation**.

## Decisions

### 1. Role and Permission Layering

Applied the same layered approach as the User module:

* **Schema Layer**: `schemas/roleSchema.py` and `schemas/permissionSchema.py` for validation and API-ready models
* **Provider Layer**: `Middleware/DataProvider/IdentityProvider/roleProvider.py` and `permissionProvider.py` for database access
* **Backend Layer**: `backend/identity/role.py` and `permission.py` for ports and adapters
* **Service Layer**: Adapters implement ports for use by API
* **App Layer**: FastAPI endpoints to consume identity services
* **Frontend Layer**: Planned for later integration

### 2. Immutable Role Design

* `SecurityRole` model represents **stable, internal system roles** (ops, admin, auditor)
* Roles contain a **list of permission codes**
* Roles are **immutable** to ensure security and authority consistency
* Adapter exposes read-only operations only (get by ID, name, list with optional permission filter)

### 3. Permission Model and Design

* `SecurityPermission` and `RolePermission` models created
* Permissions are **deterministic and read-only**
* `RolePermission` maps roles to granted permissions
* Avoided creating `UserRole` table; user-to-role mapping handled through joins in the provider
* Providers ensure **database isolation** and handle **all read-only queries**

### 4. Port & Adapter Pattern

* `RolePort` and `PermissionPort` define **read-only interfaces**
* Adapters implement ports and delegate to providers
* Provides a **clean contract for API layer** without exposing database logic
* `PermissionAdapter` includes:

  * `has_permission(user_id, permission)` – evaluates user authorization
  * `assert_permission(user_id, permission)` – raises `AuthorizationError` if unauthorized

### 5. Provider Decisions

* Providers handle **direct DB access using SQLModel**
* Use **joins** to resolve role-permission relationships
* `SecurityPermissionProvider` encapsulates queries like:

  * Permissions for a role
  * Roles granting a permission
* Eliminates need for explicit `UserRole` table
* Session management is injected into provider for DB operations

### 6. Validation and Safety

* Schemas validate all outputs before returning to adapters
* Ports ensure **read-only deterministic behavior**
* Immutable roles and permissions reduce risk of unauthorized modifications

### 7. Documentation and Standards

* Full PEP 257-compliant docstrings in all files
* Type hints used extensively
* Adapters and providers include **technical teaching points**
* Aligns with Aureon’s coding quality standards

## Implementation Details

### Files Created/Modified

* `models/security/role.py` – Immutable Role model
* `models/security/permission.py` – Permission and RolePermission models
* `backend/identity/role.py` – Role port & adapter
* `backend/identity/permission.py` – Permission port & adapter
* `Middleware/DataProvider/IdentityProvider/roleProvider.py` – RoleProvider
* `Middleware/DataProvider/IdentityProvider/permissionProvider.py` – PermissionProvider
* `schemas/roleSchema.py` and `schemas/permissionSchema.py` – Pydantic models
* Git commit created as checkpoint for Identity Role/Permission subsystem

### Key Features

* **Immutable roles** with stable authority mapping
* **Deterministic permission checks** via port-adapter
* **Database isolation** in providers
* **No UserRole table required**; joins performed inside providers
* **Full PEP 257-compliant documentation**
* **Type-safe, API-ready outputs** for adapters

## Consequences

* Identity module now fully supports **role-based authorization**
* Read-only role and permission system reduces risk of accidental mutations
* Providers and adapters maintain **separation of concerns** and **testability**
* Future extensions (e.g., multi-factor auth, OAuth) can integrate without breaking contracts
* System is ready for **integration with API endpoints** for user authorization

## Next Steps

* Implement API endpoints for role and permission retrieval
* Integrate PermissionAdapter into **authorization checks**
* Write unit tests for ports and adapters
* Extend identity module documentation for **authorization workflows**
* Begin integration tests combining authentication, roles, and permissions

---
