/**
 * API client for CoinPurse backend
 * Handles all HTTP requests to the FastAPI backend
 */

import type { ApiError } from './types';

// API configuration
export const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Custom error class for API errors
 */
export class ApiException extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = 'ApiException';
  }
}

/**
 * Base fetch wrapper with error handling
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    // Handle 204 No Content (delete operations)
    if (response.status === 204) {
      return undefined as T;
    }

    const data = await response.json();
    console.log(data)

    if (!response.ok) {
      const error = data as ApiError;
      throw new ApiException(response.status, error.detail || 'An error occurred');
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiException) {
      throw error;
    }
    // Network or parsing error
    throw new ApiException(0, 'Network error: Unable to connect to the API');
  }
}

/**
 * Build query string from params object
 */
export function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}