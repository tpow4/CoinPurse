/**
 * TypeScript types matching the FastAPI backend schemas
 * These correspond to the Pydantic models in backend/schemas/
 */

// Enums matching backend/models/base.py

export enum AccountType {
    BANKING = 'banking',
    TREASURY = 'treasury',
    CREDIT_CARD = 'credit_card',
    INVESTMENT = 'investment',
}

export enum TaxTreatmentType {
    TAXABLE = 'taxable',
    TAX_DEFERRED = 'tax_deferred',
    TAX_FREE = 'tax_free',
    TRIPLE_TAX_FREE = 'triple_tax_free',
    NOT_APPLICABLE = 'not_applicable',
}

export enum TransactionType {
    PURCHASE = 'purchase',
    PAYMENT = 'payment',
    REFUND = 'refund',
    TRANSFER = 'transfer',
    FEE = 'fee',
    INTEREST = 'interest',
    ADJUSTMENT = 'adjustment',
    WITHDRAWAL = 'withdrawal',
    DEPOSIT = 'deposit',
}

// Institution types

export interface Institution {
    institution_id: number;
    name: string;
    is_active: boolean;
    created_at: string;
    modified_at: string;
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
    modified_at: string;
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
    template_id: number | null;
    account_type: AccountType;
    tax_treatment: TaxTreatmentType;
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
    tax_treatment: TaxTreatmentType;
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
    tax_treatment?: TaxTreatmentType;
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

export interface TransactionWithNames extends Transaction {
    account_name: string;
    category_name: string;
}

// Balance types

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

export interface BalanceBatchCreate {
    account_id: number;
    balances: { balance_date: string; balance: number }[];
}

export interface BalanceBatchResponse {
    created: number;
    updated: number;
    balances: AccountBalance[];
}

// Aggregated monthly balance types

export interface MonthlyBalancePoint {
    balance_date: string; // ISO date string - end of month
    balance: number; // Balance in cents
}

export interface AccountBalanceSeries {
    account_id: number;
    account_name: string;
    institution_name: string;
    account_type: string;
    tax_treatment: string;
    data: MonthlyBalancePoint[];
}

export interface MonthlyBalanceAggregateResponse {
    month_end_dates: string[]; // ISO date strings - all end-of-month dates in range
    series: AccountBalanceSeries[]; // Balance time series for each account
}

export interface AggregatedMonthlyParams {
    start_date?: string; // ISO date string (YYYY-MM-DD)
    end_date?: string; // ISO date string (YYYY-MM-DD)
    include_inactive_accounts?: boolean;
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

// Import types

export enum FileFormat {
    CSV = 'csv',
    EXCEL = 'excel',
}

export enum ImportStatus {
    PREVIEW = 'preview',
    COMPLETED = 'completed',
    FAILED = 'failed',
}

export interface ImportTemplate {
    template_id: number;
    template_name: string;
    file_format: FileFormat;
    column_mappings: Record<string, string | null>;
    amount_config: Record<string, any>;
    header_row: number;
    skip_rows: number;
    date_format: string;
    is_active: boolean;
    created_at: string;
    modified_at: string;
}

export interface ParsedTransaction {
    row_number: number;
    transaction_date: string | null;
    posted_date: string | null;
    description: string;
    amount: number; // Amount in cents
    transaction_type: string; // CREDIT or DEBIT
    category_name: string | null;
    coinpurse_category_id: number | null;
    candidate_category_ids: number[];
    is_duplicate: boolean;
    validation_errors: string[];
}

export interface ImportPreviewSummary {
    total_rows: number;
    valid_rows: number;
    duplicate_count: number;
    validation_errors: number;
}

export interface ImportPreviewResponse {
    import_batch_id: number;
    summary: ImportPreviewSummary;
    transactions: ParsedTransaction[];
}

export interface ImportConfirmRequest {
    import_batch_id: number;
    selected_rows: number[];
    category_overrides?: Record<number, number>; // row_number → category_id
}

export interface ImportConfirmResponse {
    import_batch_id: number;
    imported_count: number;
    skipped_count: number;
    duplicate_count: number;
    status: ImportStatus;
}

// Helper types

export interface ApiError {
    detail: string;
}
