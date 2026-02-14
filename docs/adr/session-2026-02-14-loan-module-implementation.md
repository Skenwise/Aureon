# ADR-2026-02-08: Loan Module - Complete Architecture & Implementation

**Title:** Loan Module: Contracts, Schedules, Disbursements, Repayments, and Interest Calculation

**Date:** 2026-02-08

**Status:** Accepted

---

## Context

We needed a complete loan management system for the Aureon backend that can:
* Define and manage loan contracts with state machine lifecycle
* Generate and track repayment schedules with amortization
* Execute loan disbursements (coordinate with treasury, payments, accounting)
* Process loan repayments with payment allocation
* Calculate interest using multiple methods (simple, compound, amortized)

The loan module is a **product layer** built on top of accounting, treasury, and payments modules. It defines credit obligations and manages their complete lifecycle without directly moving money or creating accounting entries.

---

## Architecture Decisions

### 1. **Port & Adapter Pattern**

**Decision:** Use Port & Adapter architecture for all database operations.

**Reasoning:**
- Separates business logic from persistence
- Allows testing without database
- Enables future provider swaps
- Maintains consistency with treasury and accounting modules

**Implementation:**
- **Ports (Protocol):** Define interfaces for operations
- **Adapters:** Implement ports, delegate to providers
- **Providers:** Handle database operations only

---

### 2. **Five-File Structure**

**Decision:** Split loan module into 5 backend files:

```
backend/loans/
├── loan.py              # Loan contract operations
├── schedule.py          # Repayment schedule generation
├── interest.py          # Interest calculation (pure logic)
├── disbursement.py      # Loan funding operations
└── repayment.py         # Payment application
```

**Reasoning:**
- Each file has a single, clear responsibility
- Interest is pure calculation (no database) - no port/adapter needed
- Disbursement and repayment orchestrate multiple modules
- Clear separation of concerns

---

### 3. **Schemas Layer**

**Decision:** Single unified schema file for all loan operations.

**File:** `schemas/loanSchema.py`

**Schemas Created:**
- `LoanCreate` / `LoanUpdate` / `LoanRead`
- `ScheduleCreate` / `ScheduleInstallmentRead` / `ScheduleRead`
- `DisbursementCreate` / `DisbursementRead`
- `RepaymentCreate` / `RepaymentRead`
- `InterestCalculationRequest` / `InterestCalculationResult`

**Reasoning:**
- All loan-related schemas in one place
- Clear data contracts at module boundaries
- Pydantic validation ensures type safety
- Easy to maintain and extend

---

### 4. **Database Models**

**Decision:** Four database models for loan persistence.

**Models Created:**
```
database/model/finance/
├── loan.py                    # Loan contract
├── loan_schedule.py           # Repayment installments
├── loan_disbursement.py       # Disbursement records (NEW)
└── loan_repayment.py          # Repayment records (NEW)
```

**Relationships:**
- `Loan` has many `LoanSchedule`, `LoanDisbursement`, `LoanRepayment`
- `LoanDisbursement` links to `Account` (disbursement target)
- `LoanDisbursement` and `LoanRepayment` link to `Journal` (accounting entries)
- All models support multi-tenancy via `Company` relationship

---

### 5. **Loan State Machine**

**Decision:** Explicit state transitions with validation.

**States:**
```
PENDING → DISBURSED → ACTIVE → CLOSED
                       ↓
                   DEFAULTED
```

**Valid Transitions:**
- `PENDING → DISBURSED` (after disbursement execution)
- `DISBURSED → ACTIVE` (loan becomes active)
- `ACTIVE → CLOSED` (fully repaid)
- `ACTIVE → DEFAULTED` (borrower failed to repay)

**Reasoning:**
- Prevents invalid state changes
- Makes lifecycle explicit and auditable
- Enables proper business logic enforcement

---

### 6. **Interest Calculation (Pure Logic)**

**Decision:** Interest calculator is pure domain logic, no database operations.

**Class:** `InterestCalculator` (static methods only)

**Methods:**
- `calculate_simple_interest()`
- `calculate_monthly_payment()`
- `calculate_total_interest()`
- `calculate()` - main entry point using schemas

**Reasoning:**
- Interest is deterministic calculation
- No state, no side effects
- Easy to test
- No need for port/adapter pattern

---

### 7. **Providers Layer**

**Decision:** Four providers for database operations.

**Providers Created:**
```
Middleware/DataProvider/LoanProvider/
├── loanProvider.py
├── scheduleProvider.py
├── disbursementProvider.py
└── repaymentProvider.py
```

**Key Responsibilities:**

**LoanProvider:**
- Create loan contracts
- Update loan status (state machine)
- Generate unique loan numbers
- List loans with filters

**ScheduleProvider:**
- Generate complete repayment schedules
- Calculate amortization using formula: `M = P * [r(1+r)^n] / [(1+r)^n - 1]`
- Update installment status
- Track next due installment

**DisbursementProvider:**
- Create disbursement records
- Update disbursement status
- Track execution state
- **NOTE:** Does not execute fund transfers (orchestration happens at adapter layer)

**RepaymentProvider:**
- Create repayment records
- Update repayment status
- Track payment application
- **NOTE:** Does not allocate payments (orchestration happens at adapter layer)

---

### 8. **Type Safety with `require()` Utility**

**Decision:** Use `require()` helper for safe type casting.

**Implementation:**
```python
from backend.core.utils import require

# Extract and validate
borrower_id = require(loan_data, "borrower_id", UUID)
principal_amount = require(loan_data, "principal_amount", float)
```

**Reasoning:**
- Fixes Pylance type checking errors
- Runtime validation with clear error messages
- Consistent error handling across all providers
- Type-safe at both compile-time and runtime

---

### 9. **Orchestration Separation**

**Decision:** Providers handle persistence only. Orchestration happens at adapter/service layer.

**Provider Responsibilities (Database Only):**
- CRUD operations
- Status updates
- Query filtering

**Adapter Responsibilities (Orchestration):**
- Coordinate with treasury for liquidity checks
- Coordinate with payments for fund transfers
- Coordinate with accounting for journal entries
- Update multiple entities atomically

**Example Flow (Disbursement):**
```
Adapter.execute_disbursement():
  1. Check treasury liquidity
  2. Execute payment via payments module
  3. Create accounting journal entry
  4. Update loan status (PENDING → DISBURSED → ACTIVE)
  5. Call provider.execute_disbursement() to mark COMPLETED
```

**Reasoning:**
- Clear separation of concerns
- Providers remain simple and testable
- Business logic lives in adapters
- Enables complex workflows without polluting providers

---

### 10. **Schedule Generation Algorithm**

**Decision:** Use standard amortization formula with proper calculation.

**Formula:**
```
M = P * [r(1+r)^n] / [(1+r)^n - 1]

Where:
M = Monthly payment
P = Principal
r = Monthly interest rate (annual_rate / 100 / 12)
n = Number of months
```

**Implementation Details:**
- Handles 0% interest rate edge case
- Calculates interest-first allocation
- Tracks remaining principal per installment
- Supports multiple payment frequencies (MONTHLY, WEEKLY, BIWEEKLY)

---

## Files Created

### Backend Layer (Ports & Adapters)
```
backend/loans/loan.py
backend/loans/schedule.py
backend/loans/interest.py
backend/loans/disbursement.py
backend/loans/repayment.py
```

### Provider Layer
```
Middleware/DataProvider/LoanProvider/loanProvider.py
Middleware/DataProvider/LoanProvider/scheduleProvider.py
Middleware/DataProvider/LoanProvider/disbursementProvider.py
Middleware/DataProvider/LoanProvider/repaymentProvider.py
Middleware/DataProvider/LoanProvider/__init__.py
```

### Schema Layer
```
schemas/loanSchema.py
```

### Database Models (Updated/Created)
```
database/model/finance/loan.py (updated)
database/model/finance/loan_schedule.py (updated)
database/model/finance/loan_disbursement.py (NEW)
database/model/finance/loan_repayment.py (NEW)
database/model/finance/__init__.py (updated)
```

---

## Consequences

### Positive
✅ **Complete loan lifecycle management** from creation to closure  
✅ **Clean architecture** with clear separation of concerns  
✅ **Type-safe** with Pydantic schemas and `require()` utility  
✅ **Testable** - pure logic separated from database operations  
✅ **Extensible** - easy to add new loan products or calculation methods  
✅ **Audit-ready** - full state machine tracking and history  
✅ **Consistent** with treasury and accounting module patterns  

### Negative
⚠️ **Orchestration complexity** - disbursement/repayment require coordination across multiple modules  
⚠️ **Payment allocation logic** - needs proper implementation for complex scenarios  
⚠️ **Performance considerations** - schedule generation for long-term loans  

---

## Outstanding Implementation Tasks

### High Priority
1. **Disbursement orchestration:**
   - Implement `DisbursementAdapter.execute_disbursement()` coordination
   - Integrate with treasury liquidity checks
   - Integrate with payments module for fund transfer
   - Create accounting journal entries (Debit: Loan Receivable, Credit: Cash)

2. **Repayment orchestration:**
   - Implement `RepaymentAdapter.apply_repayment()` coordination
   - Build payment allocation algorithm (interest first, then principal)
   - Update schedule installments
   - Create accounting journal entries (Debit: Cash, Credit: Loan Receivable + Interest Income)

3. **Payment allocation algorithm:**
   - Handle partial payments
   - Handle overpayments
   - Handle multiple installment coverage
   - Support payment priority rules

### Medium Priority
4. **Schedule enhancements:**
   - Support grace periods
   - Support balloon payments
   - Support irregular payment schedules
   - Support payment frequency changes

5. **Loan product variations:**
   - Support interest-only loans
   - Support decreasing balance method
   - Support flat interest rate
   - Support custom amortization schedules

### Low Priority
6. **Advanced features:**
   - Loan refinancing
   - Loan restructuring
   - Early closure with penalty calculation
   - Late fee calculation and application

---

## Testing Requirements

### Unit Tests Needed
- Interest calculator (all calculation methods)
- Schedule generation (various terms, rates, frequencies)
- State machine transitions (valid and invalid)
- Payment allocation logic

### Integration Tests Needed
- Disbursement flow (loan → treasury → payments → accounting)
- Repayment flow (payments → schedule → accounting → loan)
- Multi-installment repayment
- Loan closure scenarios

### Edge Cases to Test
- Zero interest rate loans
- Very long term loans (360+ months)
- Partial payments
- Overpayments
- Payment reversals
- Schedule regeneration

---

## Dependencies

### Module Dependencies
- ✅ **accounting** - journal entry creation
- ✅ **treasury** - liquidity checks and fund availability
- ✅ **payments** - fund transfer execution
- ✅ **currency** - currency validation
- ✅ **core.money** - money value object
- ✅ **core.time** - date operations
- ✅ **core.utils** - `require()` helper
- ✅ **core.errors** - error handling

### External Dependencies
- `dateutil.relativedelta` - date calculation for schedules
- `pydantic` - schema validation
- `sqlmodel` - database operations

---

## Migration Path

### From Existing System
If migrating from an existing loan system:

1. **Data migration:**
   - Map existing loan records to new `Loan` model
   - Generate schedules for active loans
   - Create historical disbursement/repayment records

2. **Status mapping:**
   - Map old statuses to new state machine
   - Handle edge cases (partially disbursed, etc.)

3. **Schedule reconciliation:**
   - Verify installment calculations match
   - Handle any discrepancies with adjustments

---

## Related ADRs
- ADR-2026-02-02: Accounting Module
- ADR-2026-02-13: Treasury Module
- (Future) ADR: Payments Module
- (Future) ADR: Financial Reporting

---

## Notes

**Design Philosophy:**
> "Loans define obligations, not execution. They instruct other modules on what should happen, but never execute directly."

This principle ensures:
- Clear separation of concerns
- Accounting integrity maintained
- Treasury controls real money
- Payments execute movement
- Loans remain the source of truth for obligations

---

**Approved By:** Architecture Team  
**Implementation Status:** Complete (awaiting orchestration logic)  
**Next Module:** Payments Module