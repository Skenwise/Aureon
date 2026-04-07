I'll create comprehensive MD files that document the complete system requirements and architecture for Aureon as a full-fledged banking system.

---

## File 1: `docs/system-requirements.md`

```markdown
# Aureon System Requirements — Complete Banking & Lending Platform

## System Overview

Aureon is a **double-entry core banking system** designed for microfinance institutions, SACCOs, and community banks. It provides end-to-end loan lifecycle management, treasury operations, payment processing, and regulatory compliance.

### Core Capabilities
- **Double-Entry Accounting** — Immutable ledger with GAAP/IFRS compliance
- **Loan Management** — Full lifecycle from origination to write-off
- **Payment Processing** — Multiple payment rails (Internal, Mobile Money, Bank Transfers)
- **Treasury Management** — Liquidity tracking, fund reservations, cash positions
- **Multi-Tenancy** — Isolated data per financial institution
- **Audit Trail** — Complete, immutable record of all actions
- **Reporting** — Financial statements, regulatory reports, portfolio analytics

---

## Module 1: Authentication & Identity

### User Types
| Role | Description | Permissions |
|------|-------------|-------------|
| **Super Admin** | System administrator | Full system access, tenant management |
| **Tenant Admin** | Institution administrator | Manage users, view all reports, approve loans |
| **Loan Officer** | Frontline staff | Create loans, process repayments, view assigned portfolio |
| **Treasury Officer** | Cash management | Manage fund reservations, approve payments |
| **Accountant** | Financial operations | Post journals, reconcile accounts, generate reports |
| **Auditor** | Compliance | Read-only audit trail access |
| **Borrower** | Customer | View own loans, make repayments (via portal) |

### Authentication Operations
| Operation | Description | Modules |
|-----------|-------------|---------|
| Login | Authenticate user with email/password | Identity, Audit |
| Logout | Invalidate session | Identity, Audit |
| Refresh Token | Renew JWT access token | Identity |
| Change Password | User-initiated password change | Identity, Audit |
| Reset Password | Forgot password flow | Identity, Audit |
| Create User | Admin creates new user | Identity, Tenants, Audit |
| Update User | Modify user details | Identity, Audit |
| Deactivate User | Disable user account | Identity, Audit |
| Assign Role | Set user permissions | Identity, Tenants, Audit |
| Get Current User | Return authenticated user context | Identity |
| List Users | Paginated user list with filters | Identity, Tenants |

---

## Module 2: Tenant Management

### Institution Operations
| Operation | Description | Modules |
|-----------|-------------|---------|
| Create Tenant | Register new financial institution | Tenants, Identity, Audit |
| Update Tenant | Modify institution details | Tenants, Audit |
| Get Tenant | Retrieve institution information | Tenants |
| List Tenants | Paginated institution list (Super Admin only) | Tenants |
| Configure Settings | Institution-specific settings (currency, timezone, fees) | Tenants, Audit |

---

## Module 3: Chart of Accounts & Accounting

### Account Types (Standard Banking COA)
| Account Class | Account Types | Normal Balance |
|---------------|---------------|----------------|
| **ASSET** | Cash, Bank Accounts, Loans Receivable, Interest Receivable, Accounts Receivable, Fixed Assets | DEBIT |
| **LIABILITY** | Deposits, Loans Payable, Interest Payable, Accounts Payable, Accrued Expenses | CREDIT |
| **EQUITY** | Capital, Retained Earnings, Current Year Earnings | CREDIT |
| **INCOME** | Interest Income, Fee Income, Penalty Income, Other Income | CREDIT |
| **EXPENSE** | Interest Expense, Operating Expense, Bad Debt Expense, Depreciation | DEBIT |

### Accounting Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Create Account | Create new ledger account | Accounting, Audit |
| Update Account | Modify account details | Accounting, Audit |
| Deactivate Account | Prevent further posting | Accounting, Audit |
| List Accounts | View chart of accounts | Accounting |
| Create Journal Entry | Draft double-entry transaction | Accounting, Audit |
| Post Journal Entry | Commit to ledger, update balances | Accounting, Audit |
| Reverse Journal Entry | Create reversing entries | Accounting, Audit |
| Get Journal Entry | Retrieve entry with lines | Accounting |
| List Journals | Filtered journal entries | Accounting |
| Get Account Balance | Current balance with history | Accounting |
| Get Trial Balance | All accounts with balances | Accounting, Reporting |
| Get Balance Sheet | Assets = Liabilities + Equity | Accounting, Reporting |
| Get Income Statement | Revenue - Expenses = Net Income | Accounting, Reporting |
| Get Cash Flow Statement | Operating, Investing, Financing | Accounting, Reporting |

---

## Module 4: Loan Management

### Loan Products
| Product Type | Description | Interest Calculation |
|--------------|-------------|---------------------|
| **Personal Loan** | Unsecured consumer lending | Amortized (Monthly) |
| **Business Loan** | SME working capital | Amortized or Bullet |
| **Emergency Loan** | Short-term urgent funds | Simple interest |
| **Agricultural Loan** | Seasonal farming cycles | Interest-only with balloon |
| **Education Loan** | Tuition financing | Amortized with grace period |
| **Group Loan** | Village banking model | Amortized with joint liability |

### Loan Lifecycle States
```
PENDING → APPROVED → DISBURSED → ACTIVE → CLOSED
                    ↓
                DEFAULTED → WRITTEN_OFF
```

### Loan Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Create Loan Application | Submit loan request | Loans, Identity, Audit |
| Approve Loan | Credit committee approval | Loans, Audit |
| Reject Loan | Decline with reason | Loans, Audit |
| Disburse Loan | Transfer funds to borrower | Loans, Treasury, Payments, Accounting, Audit |
| Process Repayment | Apply payment to loan | Loans, Payments, Accounting, Treasury, Audit |
| Calculate Interest | Accrue interest (daily/monthly) | Loans, Accounting |
| Generate Schedule | Create repayment plan | Loans |
| Restructure Loan | Modify terms (extension, forbearance) | Loans, Accounting, Audit |
| Write Off Loan | Remove unrecoverable loan | Loans, Accounting, Audit |
| Get Loan Details | Full loan information | Loans |
| List Loans | Filtered portfolio view | Loans |
| Get Loan Balance | Outstanding principal + interest | Loans, Accounting |
| Get Repayment History | All payments applied | Loans, Payments |
| Get Aging Report | Overdue categorization | Loans, Reporting |

---

## Module 5: Payment Processing

### Payment Types
| Type | Direction | Description | Examples |
|------|-----------|-------------|----------|
| **Outbound** | OUT | Money leaving system | Loan disbursement, withdrawal, external transfer |
| **Inbound** | IN | Money entering system | Loan repayment, deposit, incoming transfer |
| **Settlement** | INTERNAL | Internal movement | Inter-account transfer, treasury allocation |

### Payment Providers
| Provider | Type | Description |
|----------|------|-------------|
| **Internal** | Ledger-only | No external network, instant settlement |
| **MTN Mobile Money** | Mobile | Zambia mobile money |
| **Airtel Money** | Mobile | Zambia mobile money |
| **Bank Transfer** | Bank | ACH, Wire, RTGS |
| **Cash** | Physical | Cash handling (with teller module) |

### Payment Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Create Outbound Payment | Initiate payment request | Payments, Treasury, Accounting, Audit |
| Execute Outbound Payment | Call provider API | Payments, Accounting, Audit |
| Create Inbound Payment | Record incoming payment | Payments, Treasury, Accounting, Audit |
| Verify Inbound Payment | Validate provider webhook | Payments, Accounting, Audit |
| Create Settlement | Internal fund transfer | Payments, Accounting, Audit |
| Execute Settlement | Update ledger balances | Payments, Accounting, Audit |
| Reverse Payment | Reversal of completed payment | Payments, Accounting, Audit |
| Retry Failed Payment | Automatic retry with backoff | Payments, Audit |
| Get Payment Status | Check payment state | Payments |
| List Payments | Filtered transaction history | Payments, Reporting |
| Get Provider Balance | Check external provider balance | Payments (provider-specific) |

---

## Module 6: Treasury Management

### Treasury Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Get Cash Position | Real-time balance by account | Treasury, Accounting |
| Check Liquidity | Verify sufficient funds | Treasury, Accounting |
| Reserve Funds | Lock funds for pending payment | Treasury, Accounting, Audit |
| Release Funds | Unlock reserved funds | Treasury, Accounting, Audit |
| Get Account Balance | Current available/locked balance | Treasury, Accounting |
| Get Daily Position | Start of day, end of day, net flow | Treasury, Accounting, Reporting |
| Get Float | Pending transactions in clearing | Treasury, Payments |
| Transfer Between Accounts | Internal movement | Treasury, Accounting, Audit |

---

## Module 7: Reporting & Analytics

### Financial Reports
| Report | Description | Frequency |
|--------|-------------|-----------|
| **Balance Sheet** | Assets, Liabilities, Equity | Monthly, Quarterly, Yearly |
| **Income Statement** | Revenue, Expenses, Net Income | Monthly, Quarterly, Yearly |
| **Cash Flow Statement** | Operating, Investing, Financing | Monthly, Quarterly, Yearly |
| **Trial Balance** | All accounts with debits/credits | Daily, Monthly |
| **General Ledger** | Detailed transaction history | On-demand |

### Loan Portfolio Reports
| Report | Description | Frequency |
|--------|-------------|-----------|
| **Portfolio Summary** | Total loans, outstanding, overdue | Daily, Weekly |
| **Aging Report** | Loans by days overdue | Daily, Weekly |
| **Loan Loss Provision** | Expected credit losses | Monthly |
| **Disbursement Report** | New loans by period | Daily, Weekly, Monthly |
| **Repayment Report** | Collections by period | Daily, Weekly, Monthly |
| **Interest Income Report** | Accrued and received interest | Monthly |

### Operational Reports
| Report | Description | Frequency |
|--------|-------------|-----------|
| **Payment Volume Report** | Transactions by type, volume, success rate | Daily, Weekly |
| **Provider Performance** | Success rates, response times | Daily, Monthly |
| **User Activity Report** | Login frequency, actions performed | Monthly |
| **System Health** | Uptime, errors, response times | Daily |

### Regulatory Reports
| Report | Description | Jurisdiction |
|--------|-------------|--------------|
| **Central Bank Returns** | Monthly reporting to Bank of Zambia | Zambia |
| **Anti-Money Laundering** | Suspicious transaction reports | Zambia |
| **Audit Trail Export** | Full system log for auditors | All |
| **Tax Report** | Withholding tax, VAT, corporate tax | Zambia |

---

## Module 8: Audit & Compliance

### Audit Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Log Action | Record user action with context | All modules → Audit |
| Get Audit Trail | Query logs with filters | Audit |
| Export Audit Log | Compliance format (CSV, JSON, PDF) | Audit |
| Get Entity History | Complete change history of any entity | Audit |
| Get User Activity | All actions by specific user | Audit |
| Detect Anomalies | Suspicious activity alerts | Audit (future) |

### Reconciliation Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Create Reconciliation | Start reconciliation process | Audit, Treasury, Accounting |
| Get Reconciliation | View reconciliation details | Audit |
| List Reconciliations | Filtered list | Audit |
| Resolve Discrepancy | Mark as reconciled with notes | Audit |
| Generate Reconciliation Report | Statement vs ledger comparison | Audit, Reporting |

---

## Module 9: Currency & FX

### Currency Operations
| Operation | Description | Orchestration |
|-----------|-------------|---------------|
| Create Currency | Add new currency to system | Currency, Audit |
| Update Exchange Rate | Set rate between currencies | Currency, Audit |
| Get Exchange Rate | Current rate for currency pair | Currency |
| Convert Amount | Apply exchange rate | Currency |
| FX Revaluation | Mark-to-market for foreign balances | Currency, Accounting, Audit |

---

## System Constraints & Business Rules

### Accounting Invariants
1. **Double-Entry** — Every journal entry has equal debits and credits
2. **No Deletions** — Journal entries are append-only, corrections via reversal
3. **Currency Consistency** — Postings are single-currency; FX handled in Currency module
4. **Account Balance** — Never stored, always computed from postings

### Loan Business Rules
1. **Principal Validation** — Loan amount cannot exceed available treasury funds
2. **Interest Limits** — Maximum interest rate capped by regulation (Zambia: 30% APR)
3. **Repayment Allocation** — Payments applied: Fees → Interest → Principal
4. **Grace Period** — X days before overdue status applies
5. **Minimum Payment** — Cannot be less than scheduled installment
6. **No Partial Write-Off** — Full write-off only with board approval

### Payment Business Rules
1. **Liquidity First** — Outbound payments require treasury check before execution
2. **Idempotency** — Same payment cannot be executed twice
3. **Retry Policy** — Failed payments retry 3 times with exponential backoff
4. **Settlement T+0** — Internal settlements settle immediately
5. **Provider Fallback** — If primary fails, route to backup provider

### Security Rules
1. **Multi-Tenancy** — No cross-tenant data access
2. **Role-Based Access** — Permissions strictly enforced at API layer
3. **Audit Mandatory** — All state changes logged
4. **Sensitive Data Encryption** — PII encrypted at rest

---

## API Design Principles

### RESTful Endpoints
```
/tenants          # Tenant management
/users            # User management
/auth             # Authentication
/accounts         # Chart of accounts
/journals         # Journal entries
/loans            # Loan portfolio
/payments         # Payment execution
/treasury         # Treasury operations
/reports          # Financial reports
/audit            # Audit trail
/currency         # Currency management
```

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  },
  "links": {
    "self": "/api/v1/loans?page=1",
    "next": "/api/v1/loans?page=2"
  }
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_LIQUIDITY",
    "message": "Insufficient funds for disbursement",
    "details": {
      "required": 5000.00,
      "available": 3200.00
    },
    "request_id": "req_abc123"
  }
}
```

---

## Non-Functional Requirements

### Performance
- API response time: < 200ms (p95)
- Concurrent users: 1000+
- Daily transactions: 50,000+
- Reporting queries: < 5 seconds

### Availability
- 99.9% uptime (SLA)
- Scheduled maintenance window: Sunday 02:00-04:00
- Disaster recovery: RPO < 15 minutes, RTO < 4 hours

### Security
- All traffic HTTPS/TLS 1.3
- JWT with 15-minute expiry
- Session refresh via refresh token
- Rate limiting: 100 requests/minute per user
- Audit retention: 7 years (regulatory requirement)

### Compliance
- IFRS 9 compliant (Expected Credit Loss)
- AML/KYC integration
- Data residency: Zambia (or client jurisdiction)
- Backup: Daily encrypted, offsite

---

## Integration Points

### External Systems
| System | Purpose | Integration Method |
|--------|---------|-------------------|
| **Mobile Money (MTN, Airtel)** | Payment processing | REST API, Webhooks |
| **Banking System (Zanaco, etc.)** | Bulk payments | File transfer (NACHA), API |
| **Credit Reference Bureau** | Credit checks | SOAP/REST API |
| **Central Bank (BOZ)** | Regulatory reporting | XML file upload |
| **SMS Gateway** | Notifications | REST API |
| **Email Service** | Statements, alerts | SMTP, REST API |

---

## Future Enhancements

### Phase 2
- **Savings Accounts** — Interest-bearing deposits
- **Fixed Deposits** — Term deposits with maturity
- **Mobile Banking App** — Customer self-service
- **USSD Integration** — Feature phone access

### Phase 3
- **Credit Scoring** — Automated underwriting
- **Collections Management** — Automated reminders, collections workflow
- **Fraud Detection** — ML-based anomaly detection
- **IFRS 9 Automation** — ECL calculation engine

### Phase 4
- **Multi-Currency** — Cross-currency lending
- **API Marketplace** — Third-party integrations
- **Open Banking** — Customer consent-based data sharing
```

---

## File 2: `docs/api-orchestration.md`

```markdown
# Aureon API Orchestration — Module Collaboration Guide

## Overview

Aureon's API layer orchestrates multiple backend modules behind single endpoints. This document maps each user action to the modules involved and the orchestration flow.

---

## Architecture: How Modules Collaborate

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API ENDPOINT                                       │
│                    (FastAPI route with dependency injection)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SERVICE ORCHESTRATOR                                    │
│                    (Backend Adapter — Business Logic)                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ Example: LoanAdapter.disburse()                                         │   │
│  │                                                                          │   │
│  │  1. LoanProvider.get_loan()              → Validate loan exists          │   │
│  │  2. TreasuryAdapter.check_liquidity()   → Sufficient funds?             │   │
│  │  3. TreasuryAdapter.reserve_funds()     → Lock funds                    │   │
│  │  4. PaymentAdapter.execute()            → Send money                    │   │
│  │  5. AccountingAdapter.create_journal()  → Double-entry record           │   │
│  │  6. LoanProvider.update_status()        → Mark loan ACTIVE              │   │
│  │  7. AuditAdapter.log()                  → Record everything             │   │
│  │  8. Return: { journal_id, payment_id, success }                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Endpoint Orchestration Details

### 1. Loan Disbursement — `POST /loans/{id}/disburse`

**Business Context:** After loan approval, funds must move from treasury to borrower.

**Modules Orchestrated:** Loans → Treasury → Payments → Accounting → Audit

| Step | Action | Module | Method | Failure Handling |
|------|--------|--------|--------|------------------|
| 1 | Validate loan exists and is APPROVED | Loans | `get_loan()` | Return 404/400 |
| 2 | Verify disbursement amount ≤ approved amount | Loans | Validation | Return 400 |
| 3 | Check treasury liquidity | Treasury | `check_liquidity()` | Rollback, return 422 |
| 4 | Reserve funds (lock until payment) | Treasury | `reserve_funds()` | Rollback, return 422 |
| 5 | Create outbound payment record (PENDING) | Payments | `create_outbound()` | Rollback reserves |
| 6 | Execute payment via provider (Internal/MTN/Bank) | Payments | `execute_outbound()` | Rollback, mark payment FAILED |
| 7 | Create journal entry (Dr: Loans Receivable, Cr: Bank) | Accounting | `create_journal()` | Rollback payment |
| 8 | Post journal entry to ledger | Accounting | `post_journal()` | Rollback, mark payment FAILED |
| 9 | Update loan status to ACTIVE | Loans | `update_status()` | Log warning, continue |
| 10 | Generate repayment schedule | Loans | `generate_schedule()` | Async, doesn't block |
| 11 | Log all actions | Audit | `log()` | Non-blocking |

**Transaction Boundary:** Steps 1-9 must be atomic (all-or-nothing). Use database transaction.

**Response:** `{ success, journal_entry_id, payment_id, transaction_id }`

---

### 2. Loan Repayment — `POST /loans/{id}/repay`

**Business Context:** Borrower makes payment. Money enters system, loan balance reduces.

**Modules Orchestrated:** Loans → Payments → Accounting → Treasury → Audit

| Step | Action | Module | Method | Failure Handling |
|------|--------|--------|--------|------------------|
| 1 | Validate loan exists and is ACTIVE | Loans | `get_loan()` | Return 404/400 |
| 2 | Get outstanding balance | Loans | `get_outstanding_balance()` | Return 400 if zero |
| 3 | Validate payment amount ≤ outstanding | Loans | Validation | Return 400 |
| 4 | Create inbound payment record (PENDING) | Payments | `create_inbound()` | Rollback |
| 5 | Execute payment via provider verification | Payments | `verify_inbound()` | Rollback, mark FAILED |
| 6 | Calculate principal vs interest allocation | Loans | `calculate_allocation()` | Internal |
| 7 | Create journal entry (Dr: Bank, Cr: Loans Receivable, Cr: Interest Income) | Accounting | `create_journal()` | Rollback payment |
| 8 | Post journal entry | Accounting | `post_journal()` | Rollback, mark FAILED |
| 9 | Update loan balance (reduce principal) | Loans | `update_balance()` | Log warning, continue |
| 10 | Mark installment as PAID | Loans | `update_schedule()` | Log warning, continue |
| 11 | Update treasury cash position | Treasury | `update_position()` | Non-blocking |
| 12 | Log all actions | Audit | `log()` | Non-blocking |

---

### 3. Loan Write-Off — `POST /loans/{id}/write-off`

**Business Context:** Loan is unrecoverable. Remove from active portfolio, recognize loss.

**Modules Orchestrated:** Loans → Accounting → Audit

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Validate loan status is DEFAULTED | Loans | `get_loan()` |
| 2 | Get outstanding balance | Loans | `get_outstanding_balance()` |
| 3 | Create journal entry (Dr: Bad Debt Expense, Cr: Loans Receivable) | Accounting | `create_journal()` |
| 4 | Post journal entry | Accounting | `post_journal()` |
| 5 | Update loan status to WRITTEN_OFF | Loans | `update_status()` |
| 6 | Log with reason | Audit | `log()` |

---

### 4. Create Journal Entry — `POST /journals`

**Business Context:** Accountant manually creates journal entry (adjustment, accrual, etc.)

**Modules Orchestrated:** Accounting → Audit

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Validate accounts exist | Accounting | `validate_accounts()` |
| 2 | Validate debits = credits | Accounting | `validate_balance()` |
| 3 | Create journal entry (DRAFT) | Accounting | `create_journal()` |
| 4 | Log creation | Audit | `log()` |

---

### 5. Post Journal Entry — `POST /journals/{id}/post`

**Business Context:** Commit draft journal to ledger (irreversible without reversal)

**Modules Orchestrated:** Accounting → Audit

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Validate journal exists and is DRAFT | Accounting | `get_journal()` |
| 2 | Validate still balanced | Accounting | `validate_balance()` |
| 3 | Update account balances (debit/credit) | Accounting | `update_balances()` |
| 4 | Mark journal as POSTED | Accounting | `update_status()` |
| 5 | Log posting | Audit | `log()` |

---

### 6. Create Outbound Payment — `POST /payments/outbound`

**Business Context:** Manual payment from system to external party (not loan-related)

**Modules Orchestrated:** Payments → Treasury → Accounting → Audit

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Validate source account exists | Accounting | `get_account()` |
| 2 | Check treasury liquidity | Treasury | `check_liquidity()` |
| 3 | Reserve funds | Treasury | `reserve_funds()` |
| 4 | Create payment record (PENDING) | Payments | `create_outbound()` |
| 5 | Execute via provider | Payments | `execute()` |
| 6 | Create journal entry (Dr: Destination, Cr: Source) | Accounting | `create_journal()` |
| 7 | Post journal entry | Accounting | `post_journal()` |
| 8 | Mark payment COMPLETED | Payments | `complete()` |
| 9 | Release reservation | Treasury | `release_reservation()` |
| 10 | Log | Audit | `log()` |

---

### 7. Process Inbound Webhook — `POST /webhooks/{provider}`

**Business Context:** Payment provider calls back with payment confirmation

**Modules Orchestrated:** Payments → Loans → Accounting → Treasury → Audit

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Verify webhook signature | Payments | `verify_signature()` |
| 2 | Find pending payment by provider reference | Payments | `get_by_provider_reference()` |
| 3 | If payment is loan repayment: find related loan | Loans | `get_by_payment()` |
| 4 | Create journal entry | Accounting | `create_journal()` |
| 5 | Post journal entry | Accounting | `post_journal()` |
| 6 | Update loan balance | Loans | `update_balance()` |
| 7 | Update treasury position | Treasury | `update_position()` |
| 8 | Mark payment COMPLETED | Payments | `complete()` |
| 9 | Log | Audit | `log()` |

---

### 8. Get Balance Sheet — `GET /reports/balance-sheet`

**Business Context:** Financial statement showing assets, liabilities, equity

**Modules Orchestrated:** Accounting → Reporting

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Get as-of date (today or specified) | N/A | Parse request |
| 2 | Get all accounts | Accounting | `list_accounts()` |
| 3 | Get balances as of date | Accounting | `get_balances_as_of()` |
| 4 | Group by account class (ASSET, LIABILITY, EQUITY) | Reporting | `group_by_class()` |
| 5 | Calculate totals | Reporting | `calculate_totals()` |
| 6 | Return BalanceSheetReport | N/A | Response |

---

### 9. Get Trial Balance — `GET /reports/trial-balance`

**Business Context:** All accounts with debits/credits — proves ledger balance

**Modules Orchestrated:** Accounting → Reporting

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Get as-of date | N/A | Parse |
| 2 | Get all accounts with balances | Accounting | `get_trial_balance()` |
| 3 | Verify total debits = total credits | Reporting | `validate()` |
| 4 | Return TrialBalanceReport | N/A | Response |

---

### 10. Get Audit Log — `GET /audit/logs`

**Business Context:** Compliance officer views system activity

**Modules Orchestrated:** Audit

| Step | Action | Module | Method |
|------|--------|--------|--------|
| 1 | Parse filters (user, action, date range, entity) | N/A | Query params |
| 2 | Apply tenant isolation | Audit | `filter_by_tenant()` |
| 3 | Query audit logs | Audit | `filter_logs()` |
| 4 | Apply pagination | Audit | `paginate()` |
| 5 | Return AuditExportReport | N/A | Response |

---

## Transaction Management

### When to Use Transactions

| Operation | Transaction Scope | Reasoning |
|-----------|-------------------|-----------|
| Loan Disbursement | Steps 1-9 | Money movement — all-or-nothing |
| Loan Repayment | Steps 1-9 | Money movement — all-or-nothing |
| Journal Post | Steps 1-5 | Ledger integrity |
| Payment Execution | Steps 1-9 | Funds transfer |
| Loan Write-Off | Steps 1-6 | Balance sheet change |

### When NOT to Use Transactions

| Operation | Reasoning |
|-----------|-----------|
| Get Reports | Read-only, no state change |
| List Queries | Read-only |
| Audit Log | Append-only, failure non-critical |

---

## Error Handling Strategy

### Error Categories

| Category | HTTP Status | Example | Recovery |
|----------|-------------|---------|----------|
| Validation Error | 400 | Invalid amount | Client fixes input |
| Authentication Error | 401 | Invalid token | Client re-authenticates |
| Authorization Error | 403 | Insufficient permissions | Client requests access |
| Not Found | 404 | Loan doesn't exist | Client checks ID |
| Business Rule Violation | 422 | Insufficient liquidity | Client retries later |
| External Provider Error | 502 | MTN API down | Auto-retry or notify |
| System Error | 500 | Database connection | Logged, alert ops |

### Idempotency

Endpoints that must be idempotent:
- `POST /loans/{id}/disburse` — Use idempotency key
- `POST /payments/outbound` — Use idempotency key
- `POST /journals/{id}/post` — Natural idempotency

Implementation:
```python
@router.post("/loans/{id}/disburse")
async def disburse_loan(
    idempotency_key: str = Header(...)
):
    # Check if already processed
    existing = await get_by_idempotency_key(idempotency_key)
    if existing:
        return existing
    # Process fresh
    result = await process_disbursement()
    # Store result with key
    await store_idempotency_result(idempotency_key, result)
    return result
```

---

## Dependencies Between Modules

### Module Dependency Graph

```
                    ┌─────────────┐
                    │   Identity  │
                    └──────┬──────┘
                           │ (auth)
                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Tenants   │───▶│   Backend   │◀───│    Audit    │
└─────────────┘    │   Modules   │    └─────────────┘
                   └──────┬──────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Accounting  │  │   Loans     │  │  Payments   │
└─────────────┘  └─────────────┘  └─────────────┘
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                  ┌─────────────┐
                  │  Treasury   │
                  └─────────────┘
                          │
                          ▼
                  ┌─────────────┐
                  │  Reporting  │
                  └─────────────┘
```

### Module Dependencies Table

| Module | Depends On | Reason |
|--------|------------|--------|
| **Identity** | Tenants | Users belong to tenant |
| **Loans** | Identity, Accounting, Payments, Treasury, Audit | Full lifecycle orchestration |
| **Payments** | Treasury, Accounting, Audit | Money movement |
| **Accounting** | Currency, Audit | Ledger entries |
| **Treasury** | Accounting, Audit | Balance queries |
| **Reporting** | Accounting, Loans, Payments, Audit | Data aggregation |
| **Audit** | None | Records everything |

---

## API Versioning Strategy

```
/api/v1/loans          # Current stable
/api/v2/loans          # Breaking changes
```

Version increments when:
- Breaking schema changes
- Removed endpoints
- Changed business logic affecting existing clients

---

## Next Steps

1. Implement dependency injection container
2. Build Auth module (JWT, users, roles)
3. Create base API router structure
4. Implement endpoints by priority (Loans first)
5. Add integration tests
6. Generate OpenAPI documentation
```