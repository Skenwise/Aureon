# TODO: Fix company_id field issue

## Problem
Field definition conflict between base.py and child models:
- base.py: `company_id: Optional[UUID]` (no foreign key)
- Child models: `company_id: UUID = Field(foreign_key="company.id")` (required with FK)

## Solution
1. Update `base.py` - Add foreign key to company_id field
2. Remove redundant company_id definitions from child models:
   - [ ] database/model/core/user.py
   - [ ] database/model/core/customer.py
   - [ ] database/model/finance/loan.py
   - [ ] database/model/audit/audit_log.py
   - [ ] database/model/audit/reconciliation.py
   - [ ] database/model/payments/subscription.py
   - [ ] database/model/payments/transactions_external.py

## Files to Modify
1. database/model/base.py
2. database/model/core/user.py
3. database/model/core/customer.py
4. database/model/finance/loan.py
5. database/model/audit/audit_log.py
6. database/model/audit/reconciliation.py
7. database/model/payments/subscription.py
8. database/model/payments/transactions_external.py
