# ADR-2026-02-02-accounting-module

## Status

Accepted

## Context

We needed a **full accounting module** for Aureon capable of:

* Ledger account management
* Immutable, deterministic balance calculations
* Audit-ready reporting (single account, period, and trial balances)

The module had to:

* Follow **Port & Adapter architecture**
* Avoid business logic leaking into adapters
* Be currency-aware using the Money value object
* Handle all core posting/journal interactions

This module serves as the backbone for all **financial computations**, preparing the system for loan management, payments, and multi-currency accounting.

## Decisions

### 1. Core Responsibilities

The module exposes three main services:

* `AccountBalance` → snapshot of a single ledger account
* `PeriodBalance` → opening, debits, credits, and closing over a date range
* `TrialBalance` → aggregates all accounts, validates double-entry integrity

All services are **read-only**, deterministic, and audit-ready.

### 2. Database & Adapters

Adapters abstract the persistence layer:

* `AccountAdapter` → fetch ledger account metadata
* `JournalAdapter` → fetch journals and postings
* `ChartAccountAdapter` → fetch chart of accounts

**No adapters contain business logic** — they only expose immutable data for computations.

### 3. Port vs Adapter Choice

Although the architecture supports ports:

* Balance calculations currently **consume adapters directly** for simplicity
* Core logic is **decoupled from DB** and only uses adapters as immutable sources
* Ports can be introduced later if we need multiple storage backends

### 4. Core Value Objects

* `Money` → used for currency-aware arithmetic
* All arithmetic is **deterministic** and **overflow/underflow checked**
* Prevents currency mismatches by enforcing checks in each service

### 5. Schemas Layer

* `AccountBalanceRead` → single account
* `PeriodBalanceRead` → period snapshot
* `TrialBalanceItem` → per-account trial balance line
* `TrialBalanceRead` → full trial balance

Schemas are **used only at module boundaries** to isolate core logic.

### 6. Error Handling

Domain errors defined and enforced:

* `ValidationError` → input, date, or currency inconsistencies
* `CalculationError` → failed arithmetic or trial balance mismatch

Adapters do not catch errors — domain truth flows upward.

### 7. Auditing & Determinism

* All computations **immutable**
* Journals and postings are **source of truth**
* Supports **full audit trails** for all balance types

### 8. Completed Files & Implementation

* `backend/Accounting/account.py` → `AccountAdapter` + `AccountBalance`
* `backend/Accounting/balance.py` → `AccountBalance`, `PeriodBalance`, `TrialBalance`
* `backend/Accounting/chart_of_accounts.py` → `ChartAccountAdapter`
* `backend/Accounting/journal.py` → `JournalAdapter`
* `schemas/balanceSchema.py` → Pydantic schemas
* `schemas/journalSchema.py` → Journal/Postings schemas

### 9. What Was Explicitly Not Done

* Full port-based abstraction (we used adapters directly)
* Integration with multi-company or multi-currency consolidation
* Performance optimization or caching
* Accounting transactions (write-side logic)

## Outcome

A **production-ready, deterministic accounting module** that:

* Computes single account, period, and trial balances
* Is audit-ready, currency-aware, and cleanly decoupled from storage
* Serves as a foundation for **loan management, payments, and financial reporting**