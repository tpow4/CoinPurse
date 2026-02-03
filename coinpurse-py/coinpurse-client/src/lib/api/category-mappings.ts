import { apiFetch, buildQueryString } from "$lib/api";
import type { CategoryMapping, CategoryMappingCreate, CategoryMappingUpdate } from "$lib/types";

export const categoryMappingsApi = {
  /**
   * Get all category mappings, optionally filtered by institution
   */
  getAll(institutionId?: number, includeInactive = false): Promise<CategoryMapping[]> {
    const query = buildQueryString({
      institution_id: institutionId,
      include_inactive: includeInactive,
    });
    return apiFetch<CategoryMapping[]>(`/import/category-mappings${query}`);
  },

  /**
   * Get category mapping by ID
   */
  getById(id: number): Promise<CategoryMapping> {
    return apiFetch<CategoryMapping>(`/import/category-mappings/${id}`);
  },

  /**
   * Create new category mapping
   */
  create(data: CategoryMappingCreate): Promise<CategoryMapping> {
    return apiFetch<CategoryMapping>('/import/category-mappings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update category mapping
   */
  update(id: number, data: CategoryMappingUpdate): Promise<CategoryMapping> {
    return apiFetch<CategoryMapping>(`/import/category-mappings/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete category mapping (soft delete by default)
   */
  delete(id: number, hardDelete = false): Promise<void> {
    const query = buildQueryString({ hard_delete: hardDelete });
    return apiFetch<void>(`/import/category-mappings/${id}${query}`, {
      method: 'DELETE',
    });
  },
};
