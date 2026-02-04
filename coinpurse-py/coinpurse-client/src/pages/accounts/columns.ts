import type { ColumnDef } from '@tanstack/table-core';
import type { Account } from '$lib/types';
import { renderComponent } from '$lib/components/ui/data-table/render-helpers.js';
import AccountsTableActions from './accounts-table-actions.svelte';
import * as m from '$lib/paraglide/messages';
import { formatDate } from '$lib/format';

// Extended account type with institution name for display
export interface AccountWithInstitution extends Account {
    institution_name: string;
}

interface ColumnsOptions {
    onEdit: (account: Account) => void;
    onDelete: (account: Account) => void;
}

// Helper to format account type for display
function formatAccountType(type: string): string {
    return type
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

export function createColumns(
    options: ColumnsOptions
): ColumnDef<AccountWithInstitution>[] {
    return [
        {
            accessorKey: 'account_name',
            header: m.acct_col_name(),
        },
        {
            accessorKey: 'institution_name',
            header: m.acct_col_institution(),
        },
        {
            accessorKey: 'account_type',
            header: m.acct_col_type(),
            cell: ({ row }) => {
                const type = row.getValue('account_type') as string;
                return formatAccountType(type);
            },
        },
        {
            accessorKey: 'tax_treatment',
            header: m.acct_col_tax(),
            cell: ({ row }) => {
                const treatment = row.getValue('tax_treatment') as string;
                return formatAccountType(treatment);
            },
        },
        {
            accessorKey: 'last_4_digits',
            header: m.acct_col_last4(),
            cell: ({ row }) => {
                const last4 = row.getValue('last_4_digits') as string;
                return last4 || '-';
            },
        },
        {
            accessorKey: 'tracks_transactions',
            header: m.acct_col_tracks_txns(),
            cell: ({ row }) => {
                const tracks = row.getValue('tracks_transactions') as boolean;
                return tracks ? m.acct_col_yes() : m.acct_col_no();
            },
        },
        {
            accessorKey: 'tracks_balances',
            header: m.acct_col_tracks_bal(),
            cell: ({ row }) => {
                const tracks = row.getValue('tracks_balances') as boolean;
                return tracks ? m.acct_col_yes() : m.acct_col_no();
            },
        },
        {
            accessorKey: 'active',
            header: m.acct_col_status(),
            cell: ({ row }) => {
                const isActive = row.getValue('active') as boolean;
                return isActive ? m.acct_col_status_active() : m.acct_col_status_inactive();
            },
        },
        {
            accessorKey: 'created_at',
            header: m.acct_col_created(),
            cell: ({ row }) => {
                return formatDate(row.getValue('created_at') as string);
            },
        },
        {
            id: 'actions',
            header: m.acct_col_actions(),
            cell: ({ row }) => {
                return renderComponent(AccountsTableActions, {
                    account: row.original,
                    onEdit: options.onEdit,
                    onDelete: options.onDelete,
                });
            },
        },
    ];
}
