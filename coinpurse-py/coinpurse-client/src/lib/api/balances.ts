import { apiFetch, buildQueryString } from '../api';
import type {
  AccountBalance,
  BalanceCreate,
  BalanceBatchCreate,
  BalanceBatchResponse,
  MonthlyBalanceAggregateResponse,
  AggregatedMonthlyParams,
} from '../types';

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

  /**
   * Get aggregated monthly balance data for all accounts
   * Returns normalized end-of-month snapshots with forward-fill
   */
  getAggregatedMonthly(params?: AggregatedMonthlyParams): Promise<MonthlyBalanceAggregateResponse> {
    const query = buildQueryString(params ?? {});
    return apiFetch<MonthlyBalanceAggregateResponse>(`/balances/aggregated/monthly${query}`);
  },

  /**
   * Create or update multiple balance records atomically
   */
  createBatch(data: BalanceBatchCreate): Promise<BalanceBatchResponse> {
    return apiFetch<BalanceBatchResponse>('/balances/batch', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};