# Currency Module – Design & Implementation

This document focuses on the **implementation of the Currency module** and its core functioning within the Aureon system.

The Currency module is responsible for **managing currencies**, **handling exchange rates**, and **revaluing balances in multi-currency environments**, while remaining independent from other product modules.

---

# Goals

* **Currency Management**
  Define supported currencies, their symbols, and decimal precision.

* **Exchange Rate Handling**
  Store, retrieve, and update FX rates for currency conversions.

* **FX Revaluation**
  Recalculate unrealized gains or losses due to currency fluctuations on balances and positions.

* **Precision & Safety**
  Ensure calculations are accurate and deterministic across the system.

---

# Design Philosophy

The Currency module follows **hexagonal (port–adapter) principles**, consistent with Aureon’s architecture.

* The **Backend Currency layer** contains the core logic.
* The **DataProvider layer** abstracts storage or external FX sources.
* Other modules consume Currency services without knowing implementation details.

Each currency file uses a **lightweight Port & Adapter approach**:

* A **Port** defines the contract used by downstream modules.
* An **Adapter** implements the port and delegates to DataProviders or external services.

This approach:

* Improves modularity
* Reduces coupling
* Limits propagation of errors
* Allows future replacement (e.g., new FX provider) without refactoring core logic

---

### Module Structure

```
backend/currency/
├── currency.py         # Core currency definitions
├── exchange_rate.py    # FX rates and conversion logic
└── fx_revaluation.py   # Unrealized gains/losses due to currency movements
```

Each file contains:

* One **Port**
* One **Adapter**

---

## Currency Definitions (`currency.py`)

### Responsibility

* Define and validate currencies
* Store ISO code, symbol, decimal precision
* Support formatting for display

### CurrencyPort

Defines the contract for:

* Retrieving currency details
* Validating supported currencies
* Formatting monetary values

### CurrencyAdapter

Implements currency logic using:

* In-memory or persistent currency definitions
* Validation rules
* Formatting utilities

CurrencyAdapter is isolated and can be replaced without affecting callers.

---

## Exchange Rates (`exchange_rate.py`)

### Responsibility

* Store, retrieve, and update FX rates
* Convert amounts between currencies

### ExchangeRatePort

Defines:

* Retrieval of exchange rates
* Conversion functions (from → to currency)
* Rate updates and history access

### ExchangeRateAdapter

Implements exchange rate handling using:

* Local database or external FX provider
* Precision-safe conversion functions
* Optional historical rate storage

---

## FX Revaluation (`fx_revaluation.py`)

### Responsibility

* Revalue balances in multi-currency accounts
* Calculate unrealized gains and losses due to FX fluctuations

### FXRevaluationPort

Defines:

* Revaluation of balances using old and current rates
* Reporting of gains/losses
* Integration hooks for accounting entries

### FXRevaluationAdapter

Implements revaluation by:

* Pulling balances from accounting or treasury modules
* Applying current and historical FX rates
* Returning deterministic gain/loss calculations

---

## Data Flow

```
Other Modules (Treasury, Accounting)
        ↓
  Currency Port
        ↓
  Currency Adapter
        ↓
  DataProvider / FX source
        ↓
 Database / External API
```

Key rule:

* **Core currency logic never depends on other product modules** (e.g., loans, payments)

---

## Error Handling

* Currency-specific errors are raised inside the Currency module
* Conversion and revaluation errors are deterministic and caught at the adapter boundary
* No raw database or external API errors propagate to downstream modules

---

## Future Extensions (Out of Scope)

* Multi-source FX provider integration
* Scheduled FX rate updates
* Support for crypto or non-standard currencies
* Dynamic currency rounding policies

These can be added without breaking existing interfaces.

---

## Final Principle

**Currency is the backbone of financial reality.
It must be precise, deterministic, and isolated from unrelated business logic.**

