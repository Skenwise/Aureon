# Pylance SQLAlchemy Fix TODO

## Overall Task
Add `# type: ignore` to .where() and .order_by() lines causing Pylance errors.

## Steps
- [x] 1. Create this TODO.md
- [x] 2. Edit IdentityProvider/permissionProvider.py (fixed)
- [ ] 3. Edit IdentityProvider/roleProvider.py (done)
- [x] 4. Edit LoanProvider/loanProvider.py (done)
- [x] 5. Edit AccountProvider/accountProvider.py (done)
- [ ] 6. Edit PaymentProvider/outboundProvider.py, inboundProvider.py, settlementProvider.py (chained wheres)
- [ ] 7. Edit TenantProvider.py, currencyProvider.py, chartOfAccountProvider.py
- [ ] 8. Edit AuditProvider/*, treasuryProvider/*, ReportingProvider/*
- [ ] 9. Edit remaining: journalProvider.py, reconciliation_provider.py, etc.
- [ ] 10. Test server: curl http://localhost:8000/health
- [ ] 11. attempt_completion

Progress: Starting with permissionProvider.py (VSCode visible)

