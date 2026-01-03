import { buildQueryString, apiFetch } from "$lib/api";
import type { Account, AccountCreate, AccountUpdate } from "$lib/types";

export const accountsApi = {
  /**
   * Get all accounts
   */
  getAll(includeInactive = false, institutionId?: number): Promise<Account[]> {
    const query = buildQueryString({
      include_inactive: includeInactive,
      institution_id: institutionId
    });
    return apiFetch<Account[]>(`/accounts${query}`);
  },

  /**
   * Get account by ID
   */
  getById(id: number): Promise<Account> {
    return apiFetch<Account>(`/accounts/${id}`);
  },

  /**
   * Search accounts by name
   */
  search(searchTerm: string): Promise<Account[]> {
    const query = buildQueryString({ q: searchTerm });
    return apiFetch<Account[]>(`/accounts/search${query}`);
  },

  /**
   * Create new account
   */
  create(data: AccountCreate): Promise<Account> {
    return apiFetch<Account>('/accounts/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update account
   */
  update(id: number, data: AccountUpdate): Promise<Account> {
    return apiFetch<Account>(`/accounts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete account (soft delete by default)
   */
  delete(id: number, hardDelete = false): Promise<void> {
    const query = buildQueryString({ hard_delete: hardDelete });
    return apiFetch<void>(`/accounts/${id}${query}`, {
      method: 'DELETE',
    });
  },
};