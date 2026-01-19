backend/
 ├── accounting/        # THE CORE (never compromise)
 │    ├── journal.py
 │    ├── posting.py
 │    ├── account.py
 │    ├── chart_of_accounts.py
 │    └── balance.py
 │
 ├── loans/             # Product layer (ledger-backed)
 │    ├── loan.py
 │    ├── schedule.py
 │    ├── interest.py
 │    ├── disbursement.py
 │    └── repayment.py
 │
 ├── payments/          # Money movement
 │    ├── inbound.py
 │    ├── outbound.py
 │    ├── providers/
 │    └── settlement.py
 │
 ├── treasury/          # 🔥 YOU MISSED THIS
 │    ├── liquidity.py
 │    ├── cash_positions.py
 │    └── funding.py
 │
 ├── currency/          # Monetary reality
 │    ├── currency.py
 │    ├── exchange_rate.py
 │    └── fx_revaluation.py
 │
 ├── tenants/           # Company isolation
 │    ├── tenant.py
 │    └── context.py
 │
 ├── identity/          # Security ≠ users
 │    ├── user.py
 │    ├── role.py
 │    ├── permission.py
 │    └── auth.py
 │
 ├── audit/             # Regulatory spine
 │    ├── audit_log.py
 │    ├── reconciliation.py
 │    └── controls.py
 │
 ├── reporting/         # Read-only projections
 │    ├── ledger_views.py
 │    ├── loan_reports.py
 │    └── compliance.py
 │
 └── core/              # Shared primitives
     ├── time.py
     ├── money.py
     ├── ids.py
     └── errors.py
