# backend/loans/interest.py
"""
Interest Calculator.
Pure domain logic for interest calculations.
NO PORT/ADAPTER PATTERN - This is calculation logic only, no database operations.
"""
from decimal import Decimal
from datetime import datetime
from schemas.loanSchema import InterestCalculationRequest, InterestCalculationResult


class InterestCalculator:
    """
    Pure interest calculation logic.
    No database operations, no external dependencies.
    All methods are deterministic and stateless.
    """

    @staticmethod
    def calculate_simple_interest(
        principal: Decimal, 
        annual_rate: Decimal, 
        term_months: int
    ) -> Decimal:
        """
        Calculate simple interest: I = P * r * t
        
        Args:
            principal (Decimal): Principal amount.
            annual_rate (Decimal): Annual interest rate (0-100).
            term_months (int): Term in months.
        
        Returns:
            Decimal: Total simple interest amount.
        """
        rate_decimal = annual_rate / Decimal("100")
        years = Decimal(term_months) / Decimal("12")
        return principal * rate_decimal * years

    @staticmethod
    def calculate_monthly_payment(
        principal: Decimal, 
        annual_rate: Decimal, 
        term_months: int
    ) -> Decimal:
        """
        Calculate monthly payment for amortized loan using formula:
        M = P * [r(1+r)^n] / [(1+r)^n - 1]
        
        Args:
            principal (Decimal): Principal amount.
            annual_rate (Decimal): Annual interest rate (0-100).
            term_months (int): Term in months.
        
        Returns:
            Decimal: Monthly payment amount.
        """
        if annual_rate == 0:
            return principal / Decimal(term_months)
        
        monthly_rate = (annual_rate / Decimal("100")) / Decimal("12")
        numerator = monthly_rate * ((1 + monthly_rate) ** term_months)
        denominator = ((1 + monthly_rate) ** term_months) - 1
        
        return principal * (numerator / denominator)

    @staticmethod
    def calculate_total_interest(
        principal: Decimal, 
        annual_rate: Decimal, 
        term_months: int,
        calculation_method: str = "AMORTIZED"
    ) -> Decimal:
        """
        Calculate total interest based on calculation method.
        
        Args:
            principal (Decimal): Principal amount.
            annual_rate (Decimal): Annual interest rate (0-100).
            term_months (int): Term in months.
            calculation_method (str): SIMPLE, COMPOUND, or AMORTIZED.
        
        Returns:
            Decimal: Total interest over loan term.
        """
        if calculation_method == "SIMPLE":
            return InterestCalculator.calculate_simple_interest(
                principal, annual_rate, term_months
            )
        elif calculation_method == "AMORTIZED":
            monthly_payment = InterestCalculator.calculate_monthly_payment(
                principal, annual_rate, term_months
            )
            total_paid = monthly_payment * Decimal(term_months)
            return total_paid - principal
        else:
            # Default to simple for unsupported methods
            return InterestCalculator.calculate_simple_interest(
                principal, annual_rate, term_months
            )

    @staticmethod
    def calculate(request: InterestCalculationRequest) -> InterestCalculationResult:
        """
        Perform interest calculation based on request parameters.
        
        Args:
            request (InterestCalculationRequest): Calculation parameters.
        
        Returns:
            InterestCalculationResult: Calculation results.
        """
        total_interest = InterestCalculator.calculate_total_interest(
            request.principal,
            request.annual_rate,
            request.term_months,
            request.calculation_method
        )
        
        monthly_payment = None
        if request.calculation_method == "AMORTIZED":
            monthly_payment = InterestCalculator.calculate_monthly_payment(
                request.principal,
                request.annual_rate,
                request.term_months
            )
        
        return InterestCalculationResult(
            principal=request.principal,
            total_interest=total_interest,
            total_amount=request.principal + total_interest,
            monthly_payment=monthly_payment,
            calculation_method=request.calculation_method,
            calculated_at=datetime.utcnow()
        )