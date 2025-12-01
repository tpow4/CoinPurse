/**
 * TypeScript types matching the FastAPI backend schemas
 * These correspond to the Pydantic models in backend/schemas/
 */

// Enums matching backend/models/base.py

export enum AccountType {
  CHECKING = "checking",
  CREDIT_CARD = "credit_card",
  SAVINGS = "savings",
  INVESTMENT = "investment",
  RETIREMENT = "retirement",
  BROKERAGE = "brokerage"
}

export enum TransactionType {
  PURCHASE = "purchase",
  PAYMENT = "payment",
  REFUND = "refund",
  TRANSFER = "transfer",
  FEE = "fee",
  INTEREST = "interest",
  ADJUSTMENT = "adjustment",
  WITHDRAWAL = "withdrawal",
  DEPOSIT = "deposit"
}

// Institution types

export interface Institution {
  institution_id: number;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InstitutionCreate {
  name: string;
}

export interface InstitutionUpdate {
  name?: string;
  is_active?: boolean;
}

// Category types

export interface Category {
  category_id: number;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  is_active?: boolean;
}

// Account types

export interface Account {
  account_id: number;
  account_name: string;
  institution_id: number;
  account_type: AccountType;
  account_subtype: string | null;
  last_4_digits: string;
  tracks_transactions: boolean;
  tracks_balances: boolean;
  active: boolean;
  display_order: number;
  created_at: string;
  modified_at: string;
}

export interface AccountCreate {
  account_name: string;
  institution_id: number;
  account_type: AccountType;
  account_subtype?: string | null;
  last_4_digits: string;
  tracks_transactions?: boolean;
  tracks_balances?: boolean;
  active?: boolean;
  display_order?: number;
}

export interface AccountUpdate {
  account_name?: string;
  institution_id?: number;
  account_type?: AccountType;
  account_subtype?: string | null;
  last_4_digits?: string;
  tracks_transactions?: boolean;
  tracks_balances?: boolean;
  active?: boolean;
  display_order?: number;
}

// Transaction types

export interface Transaction {
  transaction_id: number;
  account_id: number;
  category_id: number;
  transaction_date: string; // ISO date string
  posted_date: string; // ISO date string
  amount: number; // Amount in cents
  description: string;
  transaction_type: TransactionType;
  notes: string;
  is_active: boolean;
  created_at: string;
  modified_at: string;
}

export interface TransactionCreate {
  account_id: number;
  category_id: number;
  transaction_date: string; // ISO date string (YYYY-MM-DD)
  posted_date: string; // ISO date string (YYYY-MM-DD)
  amount: number; // Amount in cents
  description: string;
  transaction_type: TransactionType;
  notes?: string;
  is_active?: boolean;
}

export interface TransactionUpdate {
  account_id?: number;
  category_id?: number;
  transaction_date?: string;
  posted_date?: string;
  amount?: number;
  description?: string;
  transaction_type?: TransactionType;
  notes?: string;
  is_active?: boolean;
}

// Balance types (for future use)

export interface AccountBalance {
  balance_id: number;
  account_id: number;
  balance_date: string; // ISO date string
  balance: number; // Balance in cents
  created_at: string;
}

export interface BalanceCreate {
  account_id: number;
  balance_date: string;
  balance: number;
}

// API query parameters

export interface TransactionFilters {
  account_id?: number;
  category_id?: number;
  start_date?: string;
  end_date?: string;
  include_inactive?: boolean;
}

export interface SearchParams {
  q: string;
  include_inactive?: boolean;
}

// Helper types

export interface ApiError {
  detail: string;
}
