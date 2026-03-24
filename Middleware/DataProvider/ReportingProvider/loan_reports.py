#Middleware/DataProvider/ReportingProvider/loan_reports.py

"""
Loan Reports Provider.

Provides read-only aggregation of loan data for reporting.
Uses LoanProvider for source data.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from sqlmodel import Session

from Middleware.DataProvider.LoanProvider.loanProvider import LoanProvider
from schemas.reportingSchema import (
    LoanPortfolioSummary,
    LoanAgingReport
)


class LoanReportsProvider:
    """
    Provider for loan-related reports.
    """

    def __init__(self, session: Session):
        self.session = session
        self.loan_provider = LoanProvider(session)

    def get_portfolio_summary(
        self,
        company_id: UUID,
        as_of_date: date
    ) -> LoanPortfolioSummary:
        """
        Get loan portfolio summary statistics.
        """
        loans = self.loan_provider.list_loans_by_company(company_id)
        
        total_loans = len(loans)
        total_principal = Decimal("0")
        total_outstanding = Decimal("0")
        total_overdue = Decimal("0")
        total_paid = Decimal("0")
        
        for loan in loans:
            total_principal += Decimal(str(loan.principal_amount))
            
            # Calculate outstanding balance from repayments
            outstanding = Decimal(str(loan.principal_amount))
            if hasattr(loan, 'repayments') and loan.repayments:
                for repayment in loan.repayments:
                    # Use correct field: payment_amount (not amount_paid)
                    outstanding -= Decimal(str(repayment.payment_amount or 0))
            
            total_outstanding += outstanding
            
            # Check if overdue (end_date passed)
            if loan.end_date < as_of_date:
                total_overdue += outstanding
            
            # Calculate total paid from repayments
            if hasattr(loan, 'repayments') and loan.repayments:
                for repayment in loan.repayments:
                    # Use correct field: payment_amount
                    total_paid += Decimal(str(repayment.payment_amount or 0))
        
        avg_loan_size = total_principal / Decimal(str(total_loans)) if total_loans > 0 else Decimal("0")
        
        return LoanPortfolioSummary(
            tenant_id=company_id,
            as_of_date=as_of_date,
            total_loans=total_loans,
            total_principal=total_principal,
            total_interest_expected=Decimal("0"),
            total_outstanding=total_outstanding,
            total_overdue=total_overdue,
            total_paid=total_paid,
            portfolio_at_risk=0.0,
            average_loan_size=avg_loan_size,
            repayment_rate=0.0
        )

    def get_loan_aging_report(
        self,
        company_id: UUID,
        as_of_date: date
    ) -> LoanAgingReport:
        """
        Get loans grouped by days overdue.
        """
        loans = self.loan_provider.list_loans_by_company(company_id)
        
        current = []
        overdue_30_60 = []
        overdue_60_90 = []
        overdue_90_plus = []
        
        for loan in loans:
            # Calculate outstanding balance
            outstanding = Decimal(str(loan.principal_amount))
            if hasattr(loan, 'repayments') and loan.repayments:
                for repayment in loan.repayments:
                    # Use correct field: payment_amount
                    outstanding -= Decimal(str(repayment.payment_amount or 0))
            
            # Calculate overdue days
            overdue_days = 0
            if loan.end_date < as_of_date:
                overdue_days = (as_of_date - loan.end_date).days
            
            # Build borrower name from first_name + last_name
            borrower_name = "Unknown"
            if loan.customer:
                borrower_name = f"{loan.customer.first_name} {loan.customer.last_name}".strip()
            
            loan_data = {
                "loan_id": str(loan.id),
                "loan_number": loan.loan_number,
                "borrower_name": borrower_name,
                "outstanding_balance": float(outstanding)
            }
            
            if overdue_days <= 0:
                current.append(loan_data)
            elif overdue_days <= 30:
                current.append(loan_data)
            elif overdue_days <= 60:
                overdue_30_60.append(loan_data)
            elif overdue_days <= 90:
                overdue_60_90.append(loan_data)
            else:
                overdue_90_plus.append(loan_data)
        
        return LoanAgingReport(
            tenant_id=company_id,
            as_of_date=as_of_date,
            current=current,
            overdue_30_60=overdue_30_60,
            overdue_60_90=overdue_60_90,
            overdue_90_plus=overdue_90_plus
        )