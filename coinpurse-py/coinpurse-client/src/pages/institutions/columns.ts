import type { ColumnDef } from '@tanstack/table-core';
import type { Institution } from '$lib/types';
import { renderComponent } from '$lib/components/ui/data-table/render-helpers.js';
import InstitutionsTableActions from './institutions-table-actions.svelte';
import * as m from '$lib/paraglide/messages';

interface ColumnsOptions {
    onEdit: (institution: Institution) => void;
    onDelete: (institution: Institution) => void;
}

export function createColumns(
    options: ColumnsOptions
): ColumnDef<Institution>[] {
    return [
        {
            accessorKey: 'name',
            header: m.inst_col_name(),
        },
        {
            accessorKey: 'is_active',
            header: m.inst_col_status(),
            cell: ({ row }) => {
                const isActive = row.getValue('is_active') as boolean;
                return isActive
                    ? m.inst_col_status_active()
                    : m.inst_col_status_inactive();
            },
        },
        {
            accessorKey: 'created_at',
            header: m.inst_col_created(),
            cell: ({ row }) => {
                const date = new Date(row.getValue('created_at') as string);
                return date.toLocaleDateString();
            },
        },
        {
            id: 'actions',
            header: m.inst_col_actions(),
            cell: ({ row }) => {
                return renderComponent(InstitutionsTableActions, {
                    institution: row.original,
                    onEdit: options.onEdit,
                    onDelete: options.onDelete,
                });
            },
        },
    ];
}
