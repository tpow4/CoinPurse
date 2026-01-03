from enum import Enum as PyEnum

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class AccountType(str, PyEnum):
    """Types of financial accounts"""

    BANKING = "banking"
    TREASURY = "treasury"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"


class TaxTreatmentType(str, PyEnum):
    """Types of tax treatments for investment accounts"""

    TAXABLE = "taxable"
    TAX_DEFERRED = "tax_deferred"
    TAX_FREE = "tax_free"
    TRIPLE_TAX_FREE = "triple_tax_free"
    NOT_APPLICABLE = "not_applicable"


class TransactionType(str, PyEnum):
    """Types of transactions"""

    PURCHASE = "purchase"
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"
    FEE = "fee"
    INTEREST = "interest"
    ADJUSTMENT = "adjustment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
