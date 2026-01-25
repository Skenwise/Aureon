# Aureon System Architecture

## Overview
Aureon is a double-entry accounting and loan management system built with a layered architecture to ensure separation of concerns, maintainability, and scalability.

## Architecture Layers

### 1. Database Layer
- **Technology**: SQLAlchemy with SQLModel
- **Responsibility**: Handles all database operations, schema definitions, and migrations
- **Location**: `database/` module
- **Components**:
  - `database/model/`: SQLModel table definitions
  - `database/engine.py`: Database engine configuration
  - `database/sessionmaker.py`: Session management
  - `database/alembic/`: Database migrations

### 2. Provider Layer (Middleware)
- **Technology**: Custom data providers
- **Responsibility**: Abstracts database access, provides data retrieval and manipulation services
- **Location**: `Middleware/DataProvider/` module
- **Components**: Data provider classes that interface with the database layer and make data accessible to the business logic

### 3. Backend Layer
- **Technology**: Python business logic
- **Responsibility**: Contains all business logic, domain services, and core system functionality
- **Location**: `backend/` module
- **Components**:
  - `backend/accounting/`: Core accounting operations
  - `backend/loans/`: Loan management logic
  - `backend/payments/`: Payment processing
  - `backend/tenants/`: Multi-tenant management
  - `backend/identity/`: User management and authentication
  - `backend/audit/`: Audit logging and compliance
  - `backend/reporting/`: Report generation
  - `backend/currency/`: Currency and exchange rate handling
  - `backend/treasury/`: Treasury operations
  - `backend/core/`: Shared utilities and primitives

### 4. Schema Layer
- **Technology**: Pydantic/SQLModel schemas
- **Responsibility**: Defines data validation schemas, API request/response models
- **Location**: `schemas/` module
- **Components**: Create, Update, Read schemas for each domain (e.g., `schemas/tenants.py`)

### 5. App Layer
- **Technology**: FastAPI
- **Responsibility**: Handles HTTP routing, API endpoints, request/response handling
- **Location**: `app/` module (to be created)
- **Components**:
  - Route definitions
  - API versioning
  - Middleware integration
  - Dependency injection

### 6. Frontend Layer
- **Technology**: TBD (React, Vue, etc.)
- **Responsibility**: User interface and client-side logic
- **Location**: `frontend/` module (to be created)
- **Components**:
  - UI components
  - State management
  - API integration

## Data Flow
```
Frontend → App (FastAPI routes) → Backend (business logic) → Provider (data access) → Database (SQLAlchemy)
```

## Key Principles
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Direction**: Higher layers depend on lower layers, not vice versa
- **Abstraction**: Lower layers provide interfaces that higher layers consume
- **Testability**: Clear boundaries enable focused unit and integration testing
- **Maintainability**: Changes in one layer don't affect others

## Current Status
- Database layer: Implemented with initial schema
- Provider layer: Implemented for tenants (TenantProvider)
- Backend layer: Tenants module implemented with proper separation, others planned
- Schema layer: Dedicated `schemas/` module established with tenants schemas
- App layer: Not yet implemented
- Frontend layer: Not yet implemented</content>
<parameter name="filePath">/home/skenwise/dbs/Desktop/Project/Aureon/docs/architecture.md