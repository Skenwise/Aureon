# Aureon Accounting Module — Architecture & Design

## Role in the System
The Accounting module is the **foundational spine** of Aureon.

It defines **financial truth**.  
Every other module (loans, payments, treasury, reporting) either:
- **Produces accounting events**, or
- **Reads accounting state**

Nothing bypasses accounting. Nothing mutates balances directly.

If accounting is correct, Aureon is correct.

---

## Design Principles

1. **Ledger is Law**
   - All financial state is derived from ledger postings.
   - No stored balances, only computed ones.

2. **Double-Entry or Nothing**
   - Every movement is a debit and a credit.
   - Imbalance is a system error, not a business case.

3. **Immutability**
   - Journal entries are append-only.
   - Corrections happen via reversals, never edits.

4. **Separation of Concerns**
   - Accounting records facts.
   - Business logic decides *when* facts occur, not *how* they are recorded.

5. **Currency-Aware, FX-Agnostic**
   - Postings are single-currency.
   - FX logic lives in the Currency module, never inside accounting.

---

## Module Structure

```

accounting/
├── account.py
├── chart_of_accounts.py
├── journal.py
├── posting.py
└── balance.py

```

---

## Core Components

### Account (`account.py`)
Represents a ledger account.

- Has:
  - Account ID
  - Account Type (Asset, Liability, Equity, Income, Expense)
  - Currency
- Does **not** store balance

**Rule:**  
An account is a container for postings, not a calculator.

---

### Chart of Accounts (`chart_of_accounts.py`)
Defines the **structure and governance** of the ledger.

- Enforces:
  - Valid account hierarchy
  - Account classification
  - Posting eligibility rules

**Rule:**  
If an account is not in the chart, it does not exist.

---

### Journal (`journal.py`)
Represents an **atomic financial event**.

- A journal entry:
  - Has metadata (date, reference, source)
  - Groups multiple postings
  - Is committed or rejected as a whole

**Rule:**  
If it is not journaled, it did not happen.

---

### Posting (`posting.py`)
The **atomic unit of accounting truth**.

- Each posting:
  - Debits one account
  - Credits another
  - Uses the same amount and currency

**Invariants:**
- Debit == Credit
- Currency consistency
- No partial postings

**Rule:**  
All balance changes occur via postings — no exceptions.

---

### Balance (`balance.py`)
A **derived read model**.

- Computed from postings
- Supports:
  - Point-in-time balances
  - Period balances
  - Trial balances

**Rule:**  
Balance is a query, never a stored value.

---

## Dependency Boundaries

### Accounting Depends On
- `core.money`
- `core.time`
- `core.ids`
- `core.errors`
- `currency` (validation only)

### Accounting Does NOT Depend On
- Loans
- Payments
- Treasury
- Identity
- Audit
- Reporting

**Dependency direction is one-way and irreversible.**

---

## Interaction with Other Modules

- **Loans**
  - Generate journal entries (disbursement, interest accrual, repayment)

- **Payments**
  - Settle funds via postings

- **Treasury**
  - Reads balances and liquidity positions
  - Never mutates ledger state directly

- **Audit**
  - Observes journals and postings
  - Never alters accounting data

- **Reporting**
  - Projects ledger state into human-readable views

---

## Accounting Invariants (Non-Negotiable)

- No direct balance mutation
- No deletion of journal entries
- No hidden adjustments
- No cross-currency postings
- No business logic inside ledger operations

Violation of any invariant means:
**the system is lying.**

---

## Why This Architecture Exists

This design ensures Aureon is:
- Bank-grade
- Regulator-ready
- Explainable under audit
- Mathematically sound
- Product-agnostic

Everything else is built *on top* of this truth layer.
```

---

That’s the **canonical accounting doctrine** for Aureon.

Next logical Aureon-only step (when you’re ready):
**Treasury** — because once truth exists, liquidity must be managed.

