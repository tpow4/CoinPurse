"""
This file makes 'models' a package and exposes all models for easy import.
"""

# first import base (no dependencies)
from .base import AccountType, Base, FileFormat, ImportStatus, TaxTreatmentType, TransactionType

# import models with no foreign keys first
from .category import Category
from .institution import Institution

# import models that depend on Institution
from .import_template import ImportTemplate
from .category_mapping import CategoryMapping

# import models that depend on Account
from .account import Account
from .balance import AccountBalance
from .transaction import Transaction

# import models that depend on Account and ImportTemplate
from .import_batch import ImportBatch

# Export everything so you can do: from models import Institution, Account, etc.
__all__ = [
    "Base",
    "AccountType",
    "TaxTreatmentType",
    "TransactionType",
    "FileFormat",
    "ImportStatus",
    "Institution",
    "Account",
    "Category",
    "Transaction",
    "AccountBalance",
    "ImportTemplate",
    "CategoryMapping",
    "ImportBatch",
]
