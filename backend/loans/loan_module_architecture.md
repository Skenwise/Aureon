# Aureon Loans Module — Architecture & Design

## Role in the System

The Loans module is a **product layer built on top of accounting, treasury, and payments**.

It defines **credit obligations** and manages their lifecycle.

Loans do not move money directly.
Loans define **who owes what, when, and why**.

Other modules execute the physical and accounting consequences.

If accounting defines truth, loans define **future truth**.

---

## Design Principles

1. **Loan is a Contract, Not a Balance**

   * Loan stores obligation terms, not financial state.
   * Financial state exists in accounting.

2. **Schedule Defines Obligation Timeline**

   * Repayment expectations are precomputed.
   * Future obligations exist independently of payment execution.

3. **Accounting Reflects Loan Reality**

   * Disbursement, interest, and repayment generate journal entries.
   * Loans never mutate ledger balances directly.

4. **Payments Execute Loan Cash Movement**

   * Loans instruct payments.
   * Payments execute fund movement via treasury.

5. **State Machine Driven**

   * Loan lifecycle is explicit and controlled.
   * No implicit transitions.

---

## Module Structure

```
loans/
├── loan.py
├── schedule.py
├── interest.py
├── disbursement.py
└── repayment.py
```

---

## Core Components

### Loan (`loan.py`)

Defines the loan contract.

Contains:

* Loan ID
* Borrower reference
* Principal amount
* Interest rate
* Term length
* Currency
* Start date
* Status

Does NOT contain:

* Payment history
* Balance calculations
* Accounting logic

**Rule:**
Loan defines obligation, not execution.

---

### Schedule (`schedule.py`)

Defines the repayment timeline.

Generates and stores:

* Installment number
* Due date
* Principal component
* Interest component
* Total amount due
* Payment status

Purpose:

* Defines future expected cash flows
* Enables repayment tracking
* Enables delinquency detection

**Rule:**
Schedule defines when money must return.

---

### Disbursement (`disbursement.py`)

Handles loan funding.

Coordinates:

* Payment outbound execution
* Treasury liquidity consumption
* Accounting journal creation

Effects:

* Cash leaves treasury
* Loan receivable is created in accounting
* Loan status becomes ACTIVE

**Accounting example:**

```
Debit: Loan Receivable
Credit: Cash
```

**Rule:**
Disbursement converts obligation into real financial exposure.

---

### Repayment (`repayment.py`)

Handles borrower repayment.

Coordinates:

* Payment inbound processing
* Schedule installment closure
* Accounting settlement

Effects:

* Cash enters treasury
* Loan receivable decreases
* Interest income recognized

**Accounting example:**

```
Debit: Cash
Credit: Loan Receivable
Credit: Interest Income
```

**Rule:**
Repayment converts obligation into realized value.

---

### Interest (`interest.py`)

Handles interest calculation and accrual.

Responsibilities:

* Calculate interest based on principal and rate
* Generate accrual entries if required
* Support reporting and financial accuracy

Does NOT move money.

**Rule:**
Interest defines cost of capital over time.

---

## Loan Lifecycle State Machine

```
PENDING → DISBURSED → ACTIVE → CLOSED
                       ↓
                   DEFAULTED
```

### State Meaning

* **PENDING**
  Loan created but not funded

* **DISBURSED**
  Funds sent, awaiting activation

* **ACTIVE**
  Loan is live and being repaid

* **CLOSED**
  Fully repaid

* **DEFAULTED**
  Borrower failed to repay

State transitions are explicit and irreversible.

---

## Dependency Boundaries

### Loans Depends On

* accounting (journal creation)
* treasury (liquidity source)
* payments (fund movement)
* currency (currency validation)
* core.money
* core.time
* core.ids
* core.errors

---

### Loans Does NOT Depend On

* reporting
* audit
* identity internals
* accounting balance logic

Loans generate events.
Other modules observe and record.

---

## Interaction with Other Modules

### Accounting

Loans generate:

* Disbursement entries
* Repayment entries
* Interest entries

Accounting records financial truth.

---

### Treasury

Treasury provides liquidity for:

* Loan disbursement
* Repayment reception

Treasury manages actual cash state.

---

### Payments

Payments execute:

* Outbound disbursement
* Inbound repayment

Loans never move funds directly.

---

### Reporting

Reporting reads:

* Loan state
* Repayment progress
* Interest income

Reporting never mutates loan state.

---

## Loans Invariants (Non-Negotiable)

* Loan does not store financial balances
* Loan does not mutate accounting state directly
* Loan does not execute payments directly
* Loan schedule cannot contradict loan terms
* Loan cannot close unless fully repaid

Violation means financial inconsistency.

---

## Why This Architecture Exists

This design ensures Aureon can:

* Issue credit safely
* Track obligations precisely
* Maintain accounting integrity
* Scale across multiple financial products
* Support regulatory audit and financial reporting

Loans transform Aureon from infrastructure into a credit engine.

Accounting defines truth.
Treasury provides liquidity.
Payments execute movement.
Loans define obligation.
