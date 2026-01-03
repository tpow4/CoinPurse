import type { ColumnDef } from '@tanstack/table-core';
import type { Account } from '$lib/types';
import { renderComponent } from '$lib/components/ui/data-table/render-helpers.js';
import AccountsTableActions from './accounts-table-actions.svelte';

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
            header: 'Account Name',
        },
        {
            accessorKey: 'institution_name',
            header: 'Institution',
        },
        {
            accessorKey: 'account_type',
            header: 'Type',
            cell: ({ row }) => {
                const type = row.getValue('account_type') as string;
                return formatAccountType(type);
            },
        },
        {
            accessorKey: 'tax_treatment',
            header: 'Tax Treatment',
            cell: ({ row }) => {
                const treatment = row.getValue('tax_treatment') as string;
                return formatAccountType(treatment);
            },
        },
        {
            accessorKey: 'last_4_digits',
            header: 'Last 4',
            cell: ({ row }) => {
                const last4 = row.getValue('last_4_digits') as string;
                return last4 || '-';
            },
        },
        {
            accessorKey: 'tracks_transactions',
            header: 'Tracks Txns',
            cell: ({ row }) => {
                const tracks = row.getValue('tracks_transactions') as boolean;
                return tracks ? 'Yes' : 'No';
            },
        },
        {
            accessorKey: 'tracks_balances',
            header: 'Tracks Bal',
            cell: ({ row }) => {
                const tracks = row.getValue('tracks_balances') as boolean;
                return tracks ? 'Yes' : 'No';
            },
        },
        {
            accessorKey: 'active',
            header: 'Status',
            cell: ({ row }) => {
                const isActive = row.getValue('active') as boolean;
                return isActive ? 'Active' : 'Inactive';
            },
        },
        {
            accessorKey: 'created_at',
            header: 'Created',
            cell: ({ row }) => {
                const date = new Date(row.getValue('created_at') as string);
                return date.toLocaleDateString();
            },
        },
        {
            id: 'actions',
            header: 'Actions',
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
