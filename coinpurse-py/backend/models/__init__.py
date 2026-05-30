"""
This file makes 'models' a package and exposes all models for easy import.
"""

# first import base (no dependencies)
# import models that depend on Institution and ImportTemplate
from .account import Account

# import models with no foreign keys first
from .app_setting import AppSetting
from .balance import AccountBalance
from .base import (
    AccountType,
    Base,
    FileFormat,
    ImportStatus,
    TaxTreatmentType,
    TransactionType,
)
from .category import Category

# import models that depend on Institution
from .category_mapping import CategoryMapping

# import models that depend on Account and ImportTemplate
from .import_batch import ImportBatch
from .import_template import ImportTemplate
from .institution import Institution
from .transaction import Transaction

# Export everything so you can do: from models import Institution, Account, etc.
__all__ = [
    "Account",
    "AccountBalance",
    "AccountType",
    "AppSetting",
    "Base",
    "Category",
    "CategoryMapping",
    "FileFormat",
    "ImportBatch",
    "ImportStatus",
    "ImportTemplate",
    "Institution",
    "TaxTreatmentType",
    "Transaction",
    "TransactionType",
]
