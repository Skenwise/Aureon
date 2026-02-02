# ADR-2026-01-30-currency-module

## Status
Accepted

## Context
We needed a **shared, deterministic currency module** usable by both:
- **Aureon (core banking / accounting-first system)**
- **Loan Management System (product-first system)**

The module had to:
- Be infrastructure-agnostic
- Respect **Port & Adapter** architecture
- Avoid business logic leakage into adapters
- Centralize all FX logic in a single provider

## Decisions

### 1. Currency as a Core Monetary Reality
Currency was treated as a **primitive domain**, not a feature.
No system logic (loans, payments, accounting) owns currency.

### 2. Database Models (Completed)
Implemented immutable reference-style models:

- `Currency`
  - `code` (ISO, unique)
  - `name`
  - `decimals`

- `ExchangeRate`
  - `base_currency`
  - `quote_currency`
  - `rate`
  - `valid_from`
  - `valid_to`

These models are read-heavy and append-only by nature.

### 3. Provider Pattern (Completed)
Created a single `CurrencyProvider` responsible for:
- Currency lookup
- Exchange rate lookup
- FX conversion
- FX revaluation calculations

All **math + DB access** lives here.

### 4. Ports & Adapters (Completed)
Each responsibility got a **separate port**, but all adapters delegate to the same provider:

- `CurrencyPort / CurrencyAdapter`
- `ExchangeRatePort / ExchangeRateAdapter`
- `FXRevaluationPort / FXRevaluationAdapter`

This preserves:
- Single source of truth
- Clean dependency direction
- Testability

### 5. Error Handling (Completed)
Introduced and used domain errors:
- `NotFoundError`
- `CalculationError`

Adapters do not catch — they propagate domain truth upward.

### 6. Schema Layer (Completed)
Used Pydantic schemas only at the boundary:
- `CurrencyRead`
- No schemas inside providers or core logic

### 7. Architecture Enforcement
- Ports + Adapters live in the module
- Provider lives in Middleware/DataProvider
- No adapter touches DB directly
- No circular dependencies introduced

## What Was Explicitly Not Done
- No business rules (pricing, spreads, margins)
- No caching or performance optimization
- No historical FX averaging
- No regulatory logic

## Outcome
A **production-grade, reusable currency module** that:
- Is shared by Aureon and LMS
- Can scale to treasury, accounting, payments
- Is mathematically deterministic
- Respects clean architecture fully
