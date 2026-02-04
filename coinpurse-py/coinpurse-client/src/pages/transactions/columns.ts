import type { ColumnDef } from '@tanstack/table-core';
import type { TransactionWithNames } from '$lib/types';
import { formatCurrency, formatDate } from '$lib/format';
import * as m from '$lib/paraglide/messages';

// Helper to format transaction type for display
function formatTransactionType(type: string): string {
    return type
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

export function createColumns(): ColumnDef<TransactionWithNames>[] {
    return [
        {
            accessorKey: 'transaction_date',
            header: m.txn_col_date(),
            cell: ({ row }) => {
                const date = new Date(
                    row.getValue('transaction_date') as string
                );
                return formatDate(date);
            },
        },
        {
            accessorKey: 'account_name',
            header: m.txn_col_account(),
        },
        {
            accessorKey: 'description',
            header: m.txn_col_description(),
        },
        {
            accessorKey: 'category_name',
            header: m.txn_col_category(),
        },
        {
            accessorKey: 'transaction_type',
            header: m.txn_col_type(),
            cell: ({ row }) => {
                const type = row.getValue('transaction_type') as string;
                return formatTransactionType(type);
            },
        },
        {
            accessorKey: 'amount',
            header: m.txn_col_amount(),
            cell: ({ row }) => {
                const cents = row.getValue('amount') as number;
                const formatted = formatCurrency(Math.abs(cents) / 100);
                const prefix = cents < 0 ? '-' : '';
                return `${prefix}${formatted}`;
            },
        },
    ];
}
