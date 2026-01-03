"""
This file makes 'models' a package and exposes all models for easy import.
"""

# first import base (no dependencies)
# import models that depend on the above
from .account import Account
from .balance import AccountBalance
from .base import AccountType, Base, TransactionType
from .category import Category

# import models with no foreign keys first
from .institution import Institution

# import models that depend on Account
from .transaction import Transaction

# Export everything so you can do: from models import Institution, Account, etc.
__all__ = [
    "Base",
    "AccountType",
    "TransactionType",
    "Institution",
    "Account",
    "Category",
    "Transaction",
    "AccountBalance",
]
