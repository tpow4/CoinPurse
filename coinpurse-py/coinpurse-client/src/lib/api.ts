/**
 * API client for CoinPurse backend
 * Handles all HTTP requests to the FastAPI backend
 */

import type {
  Institution,
  InstitutionCreate,
  InstitutionUpdate,
  Category,
  CategoryCreate,
  CategoryUpdate,
  Account,
  AccountCreate,
  AccountUpdate,
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  AccountBalance,
  BalanceCreate,
  TransactionFilters,
  SearchParams,
  ApiError
} from './types';

// API configuration
const API_BASE_URL = 'http://localhost:8000/api';

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
async function apiFetch<T>(
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
function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

// ============================================================================
// INSTITUTIONS API
// ============================================================================

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

// ============================================================================
// CATEGORIES API
// ============================================================================

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

// ============================================================================
// ACCOUNTS API
// ============================================================================

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

// ============================================================================
// TRANSACTIONS API
// ============================================================================

export const transactionsApi = {
  /**
   * Get all transactions with optional filters
   */
  getAll(filters: TransactionFilters = {}): Promise<Transaction[]> {
    const query = buildQueryString(filters);
    return apiFetch<Transaction[]>(`/transactions${query}`);
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

// ============================================================================
// BALANCES API (for future use)
// ============================================================================

export const balancesApi = {
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

// Export convenience object with all APIs
export const api = {
  institutions: institutionsApi,
  categories: categoriesApi,
  accounts: accountsApi,
  transactions: transactionsApi,
  balances: balancesApi,
};
