from sqlalchemy.orm import DeclarativeBase
from enum import Enum as PyEnum

class Base(DeclarativeBase):
    pass
class AccountType(str, PyEnum):
    """Types of financial accounts"""
    CHECKING = "checking"
    CREDIT_CARD = "credit_card"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    RETIREMENT = "retirement"
    BROKERAGE = "brokerage"


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