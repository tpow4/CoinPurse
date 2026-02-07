"""
Pydantic schemas for AppSetting API
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppSettingUpdate(BaseModel):
    """Schema for updating a setting value"""

    setting_value: str = Field(..., min_length=1, max_length=500)


class AppSettingResponse(BaseModel):
    """Schema for returning a setting"""

    model_config = ConfigDict(from_attributes=True)

    setting_key: str
    setting_value: str
    created_at: datetime
    modified_at: datetime


class AccountDueForCheckin(BaseModel):
    """Schema for accounts that are due for a balance check-in"""

    account_id: int
    account_name: str
    institution_name: str
    last_balance_date: str | None
    days_since_last: int | None
