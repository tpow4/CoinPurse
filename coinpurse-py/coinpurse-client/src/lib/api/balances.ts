import { apiFetch, buildQueryString } from '../api';
import type { AccountBalance, BalanceCreate } from '../types';

export const balancesApi = {
  /**
   * Get all balances (optionally filtered by account)
   */
  getAll(accountId?: number): Promise<AccountBalance[]> {
    const query = buildQueryString({ account_id: accountId });
    return apiFetch<AccountBalance[]>(`/balances${query}`);
  },

  /**
   * Get balances for an account
   */
  getByAccount(accountId: number): Promise<AccountBalance[]> {
    const query = buildQueryString({ account_id: accountId });
    return apiFetch<AccountBalance[]>(`/balances${query}`);
  },

  /**
   * Create new balance record
   */
  create(data: BalanceCreate): Promise<AccountBalance> {
    return apiFetch<AccountBalance>('/balances/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};