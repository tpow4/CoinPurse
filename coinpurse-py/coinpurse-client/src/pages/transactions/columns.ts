import type { ColumnDef } from '@tanstack/table-core';
import type { TransactionWithNames } from '$lib/types';

// Helper to format transaction type for display
function formatTransactionType(type: string): string {
    return type
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Helper to format amount as currency
function formatCurrency(cents: number): string {
    const dollars = Math.abs(cents) / 100;
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(dollars);
}

export function createColumns(): ColumnDef<TransactionWithNames>[] {
    return [
        {
            accessorKey: 'transaction_date',
            header: 'Date',
            cell: ({ row }) => {
                const date = new Date(
                    row.getValue('transaction_date') as string
                );
                return date.toLocaleDateString();
            },
        },
        {
            accessorKey: 'account_name',
            header: 'Account',
        },
        {
            accessorKey: 'description',
            header: 'Description',
        },
        {
            accessorKey: 'category_name',
            header: 'Category',
        },
        {
            accessorKey: 'transaction_type',
            header: 'Type',
            cell: ({ row }) => {
                const type = row.getValue('transaction_type') as string;
                return formatTransactionType(type);
            },
        },
        {
            accessorKey: 'amount',
            header: 'Amount',
            cell: ({ row }) => {
                const cents = row.getValue('amount') as number;
                const formatted = formatCurrency(cents);
                const prefix = cents < 0 ? '-' : '';
                return `${prefix}${formatted}`;
            },
        },
    ];
}
