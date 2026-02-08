"""
Repository layer for AppSetting model
Handles all database operations for application settings
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.app_setting import AppSetting


class AppSettingRepository:
    """Repository for AppSetting database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_key(self, key: str) -> AppSetting | None:
        """Get a setting by its key"""
        return self.db.get(AppSetting, key)

    def get_all(self) -> list[AppSetting]:
        """Get all settings"""
        stmt = select(AppSetting).order_by(AppSetting.setting_key)
        return list(self.db.scalars(stmt))

    def upsert(self, key: str, value: str) -> AppSetting:
        """Create or update a setting"""
        setting = self.get_by_key(key)
        if setting:
            setting.setting_value = value
        else:
            setting = AppSetting(setting_key=key, setting_value=value)
            self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting
