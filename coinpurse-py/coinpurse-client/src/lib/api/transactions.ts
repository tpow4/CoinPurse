import { apiFetch, buildQueryString } from '../api';
import type { TransactionFilters, Transaction, TransactionWithNames, SearchParams, TransactionCreate, TransactionUpdate } from '$lib/types';

export const transactionsApi = {
  /**
   * Get all transactions with optional filters
   */
  getAll(filters: TransactionFilters = {}): Promise<Transaction[]> {
    const query = buildQueryString(filters);
    return apiFetch<Transaction[]>(`/transactions${query}`);
  },

  /**
   * Get all transactions with account and category names included
   * Ideal for grid/table display
   */
  getAllWithNames(filters: TransactionFilters = {}): Promise<TransactionWithNames[]> {
    const query = buildQueryString(filters);
    return apiFetch<TransactionWithNames[]>(`/transactions/with-names${query}`);
  },

  /**
   * Get transaction by ID
   */
  getById(id: number): Promise<Transaction> {
    return apiFetch<Transaction>(`/transactions/${id}`);
  },

  /**
   * Search transactions by description
   */
  search(params: SearchParams): Promise<Transaction[]> {
    const query = buildQueryString(params);
    return apiFetch<Transaction[]>(`/transactions/search${query}`);
  },

  /**
   * Create new transaction
   */
  create(data: TransactionCreate): Promise<Transaction> {
    return apiFetch<Transaction>('/transactions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update transaction
   */
  update(id: number, data: TransactionUpdate): Promise<Transaction> {
    return apiFetch<Transaction>(`/transactions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete transaction (soft delete by default)
   */
  delete(id: number, hardDelete = false): Promise<void> {
    const query = buildQueryString({ hard_delete: hardDelete });
    return apiFetch<void>(`/transactions/${id}${query}`, {
      method: 'DELETE',
    });
  },
};