import { getLocale } from '$lib/paraglide/runtime';

const CURRENCY_KEY = 'COINPURSE_CURRENCY';

export const SUPPORTED_CURRENCIES = [
	{ code: 'USD', label: 'US Dollar (USD)' },
	{ code: 'EUR', label: 'Euro (EUR)' },
	{ code: 'GBP', label: 'British Pound (GBP)' },
	{ code: 'CAD', label: 'Canadian Dollar (CAD)' },
	{ code: 'AUD', label: 'Australian Dollar (AUD)' },
	{ code: 'JPY', label: 'Japanese Yen (JPY)' },
	{ code: 'CHF', label: 'Swiss Franc (CHF)' },
	{ code: 'CNY', label: 'Chinese Yuan (CNY)' },
	{ code: 'MXN', label: 'Mexican Peso (MXN)' },
	{ code: 'BRL', label: 'Brazilian Real (BRL)' },
] as const;

export function getCurrency(): string {
	if (typeof localStorage === 'undefined') return 'USD';
	return localStorage.getItem(CURRENCY_KEY) ?? 'USD';
}

export function setCurrency(code: string): void {
	localStorage.setItem(CURRENCY_KEY, code);
}

export function formatCurrency(dollars: number): string {
	return new Intl.NumberFormat(getLocale(), {
		style: 'currency',
		currency: getCurrency(),
	}).format(dollars);
}

export function formatCompactCurrency(dollars: number): string {
	return new Intl.NumberFormat(getLocale(), {
		style: 'currency',
		currency: getCurrency(),
		notation: 'compact',
		compactDisplay: 'short',
		maximumFractionDigits: 1,
	}).format(dollars);
}

export function formatPercent(value: number): string {
	return new Intl.NumberFormat(getLocale(), {
		style: 'percent',
		maximumFractionDigits: 1,
	}).format(value);
}

export function formatDate(
	date: Date | string,
	options?: Intl.DateTimeFormatOptions
): string {
	const d = typeof date === 'string' ? new Date(date) : date;
	return new Intl.DateTimeFormat(getLocale(), {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		...options,
	}).format(d);
}

export function formatDateCompact(date: Date | string): string {
	const d = typeof date === 'string' ? new Date(date) : date;
	return new Intl.DateTimeFormat(getLocale(), {
		month: 'short',
		year: 'numeric',
	}).format(d);
}

export function getCurrencySymbol(): string {
	const formatted = new Intl.NumberFormat(getLocale(), {
		style: 'currency',
		currency: getCurrency(),
		currencyDisplay: 'narrowSymbol',
	}).format(0);
	// Strip digits, decimal separators, and whitespace to extract just the symbol
	return formatted.replace(/[\d.,\s\u00a0]/g, '').trim();
}
