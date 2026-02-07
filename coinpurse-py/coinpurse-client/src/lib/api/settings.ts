import { apiFetch } from "$lib/api";
import type { AppSetting, AppSettingUpdate, AccountDueForCheckin } from "$lib/types";

export const settingsApi = {
  /**
   * Get a setting by key
   */
  getByKey(key: string): Promise<AppSetting> {
    return apiFetch<AppSetting>(`/settings/${key}`);
  },

  /**
   * Create or update a setting
   */
  upsert(key: string, data: AppSettingUpdate): Promise<AppSetting> {
    return apiFetch<AppSetting>(`/settings/${key}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get accounts that are due for a balance check-in
   */
  getAccountsDueForCheckin(): Promise<AccountDueForCheckin[]> {
    return apiFetch<AccountDueForCheckin[]>('/settings/balance-checkin/due');
  },
};
