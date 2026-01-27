import { API_BASE_URL, ApiException, apiFetch, buildQueryString } from '$lib/api';
import type {
	ImportConfirmRequest,
	ImportConfirmResponse,
	ImportPreviewResponse,
	ImportTemplate,
} from '$lib/types';

export const importApi = {
	/**
	 * Get all import templates
	 */
	getTemplates(includeInactive = false): Promise<ImportTemplate[]> {
		const query = buildQueryString({ include_inactive: includeInactive });
		return apiFetch<ImportTemplate[]>(`/import/templates${query}`);
	},

	/**
	 * Get template by ID
	 */
	getTemplateById(id: number): Promise<ImportTemplate> {
		return apiFetch<ImportTemplate>(`/import/templates/${id}`);
	},

	/**
	 * Upload a file and get preview of parsed transactions
	 * Uses multipart form data instead of JSON
	 */
	async uploadAndPreview(
		file: File,
		accountId: number,
		templateId: number
	): Promise<ImportPreviewResponse> {
		const formData = new FormData();
		formData.append('file', file);
		formData.append('account_id', String(accountId));
		formData.append('template_id', String(templateId));

		const url = `${API_BASE_URL}/import/upload`;

		try {
			const response = await fetch(url, {
				method: 'POST',
				body: formData,
				// Don't set Content-Type header - browser will set it with boundary for multipart
			});

			const data = await response.json();

			if (!response.ok) {
				throw new ApiException(response.status, data.detail || 'An error occurred');
			}

			return data as ImportPreviewResponse;
		} catch (error) {
			if (error instanceof ApiException) {
				throw error;
			}
			throw new ApiException(0, 'Network error: Unable to connect to the API');
		}
	},

	/**
	 * Confirm and execute import for selected rows
	 */
	confirmImport(request: ImportConfirmRequest): Promise<ImportConfirmResponse> {
		return apiFetch<ImportConfirmResponse>('/import/confirm', {
			method: 'POST',
			body: JSON.stringify(request),
		});
	},
};
