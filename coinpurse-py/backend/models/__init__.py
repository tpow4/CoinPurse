"""
This file makes 'models' a package and exposes all models for easy import.
"""

# first import base (no dependencies)
from .base import Base, AccountType, TransactionType

# import models with no foreign keys first
from .institution import Institution
from .category import Category

# import models that depend on the above
from .account import Account

# import models that depend on Account
from .transaction import Transaction
from .balance import AccountBalance

# Export everything so you can do: from models import Institution, Account, etc.
__all__ = [
    'Base',
    'AccountType',
    'TransactionType',
    'Institution',
    'Account',
    'Category',
    'Transaction',
    'AccountBalance',
]