from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum

# Shared base for all models
Base = declarative_base()

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