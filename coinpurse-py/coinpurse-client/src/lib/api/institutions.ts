import { apiFetch, buildQueryString } from "$lib/api";
import type { Institution, InstitutionCreate, InstitutionUpdate } from "$lib/types";

export const institutionsApi = {
  /**
   * Get all institutions
   */
  getAll(includeInactive = false): Promise<Institution[]> {
    const query = buildQueryString({ include_inactive: includeInactive });
    return apiFetch<Institution[]>(`/institutions${query}`);
  },

  /**
   * Get institution by ID
   */
  getById(id: number): Promise<Institution> {
    return apiFetch<Institution>(`/institutions/${id}`);
  },

  /**
   * Search institutions by name
   */
  search(searchTerm: string, includeInactive = false): Promise<Institution[]> {
    const query = buildQueryString({ q: searchTerm, include_inactive: includeInactive });
    return apiFetch<Institution[]>(`/institutions/search${query}`);
  },

  /**
   * Create new institution
   */
  create(data: InstitutionCreate): Promise<Institution> {
    console.log('Creating institution with data:', data);
    return apiFetch<Institution>('/institutions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update institution
   */
  update(id: number, data: InstitutionUpdate): Promise<Institution> {
    return apiFetch<Institution>(`/institutions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete institution (soft delete by default)
   */
  delete(id: number, hardDelete = false): Promise<void> {
    const query = buildQueryString({ hard_delete: hardDelete });
    return apiFetch<void>(`/institutions/${id}${query}`, {
      method: 'DELETE',
    });
  },
};