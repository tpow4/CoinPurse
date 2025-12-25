import { buildQueryString, apiFetch } from "$lib/api";
import type { Category, CategoryCreate, CategoryUpdate, SearchParams } from "$lib/types";

export const categoriesApi = {
  /**
   * Get all categories
   */
  getAll(includeInactive = false): Promise<Category[]> {
    const query = buildQueryString({ include_inactive: includeInactive });
    return apiFetch<Category[]>(`/categories${query}`);
  },

  /**
   * Get category by ID
   */
  getById(id: number): Promise<Category> {
    return apiFetch<Category>(`/categories/${id}`);
  },

  /**
   * Search categories by name
   */
  search(params: SearchParams): Promise<Category[]> {
    const query = buildQueryString(params);
    return apiFetch<Category[]>(`/categories/search${query}`);
  },

  /**
   * Create new category
   */
  create(data: CategoryCreate): Promise<Category> {
    return apiFetch<Category>('/categories/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update category
   */
  update(id: number, data: CategoryUpdate): Promise<Category> {
    return apiFetch<Category>(`/categories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete category (soft delete by default)
   */
  delete(id: number, hardDelete = false): Promise<void> {
    const query = buildQueryString({ hard_delete: hardDelete });
    return apiFetch<void>(`/categories/${id}${query}`, {
      method: 'DELETE',
    });
  },
};