"""
This file makes 'models' a package and exposes all models for easy import.
"""

# first import base (no dependencies)
from .base import AccountType, Base, FileFormat, ImportStatus, TaxTreatmentType, TransactionType

# import models with no foreign keys first
from .app_setting import AppSetting
from .category import Category
from .import_template import ImportTemplate
from .institution import Institution

# import models that depend on Institution
from .category_mapping import CategoryMapping

# import models that depend on Institution and ImportTemplate
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
    "AppSetting",
    "Institution",
    "Account",
    "Category",
    "Transaction",
    "AccountBalance",
    "ImportTemplate",
    "CategoryMapping",
    "ImportBatch",
]
