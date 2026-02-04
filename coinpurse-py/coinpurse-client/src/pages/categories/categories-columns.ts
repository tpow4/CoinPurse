import type { ColumnDef } from '@tanstack/table-core';
import type { Category } from '$lib/types';
import { renderComponent } from '$lib/components/ui/data-table/render-helpers.js';
import CategoriesTableActions from './categories-table-actions.svelte';
import * as m from '$lib/paraglide/messages';
import { formatDate } from '$lib/format';

interface ColumnsOptions {
    onEdit: (category: Category) => void;
    onDelete: (category: Category) => void;
}

export function createColumns(options: ColumnsOptions): ColumnDef<Category>[] {
    return [
        {
            accessorKey: 'name',
            header: m.cat_col_name(),
        },
        {
            accessorKey: 'is_active',
            header: m.cat_col_status(),
            cell: ({ row }) => {
                const isActive = row.getValue('is_active') as boolean;
                return isActive ? m.cat_col_status_active() : m.cat_col_status_inactive();
            },
        },
        {
            accessorKey: 'created_at',
            header: m.cat_col_created(),
            cell: ({ row }) => {
                return formatDate(row.getValue('created_at') as string);
            },
        },
        {
            id: 'actions',
            header: m.cat_col_actions(),
            cell: ({ row }) => {
                return renderComponent(CategoriesTableActions, {
                    category: row.original,
                    onEdit: options.onEdit,
                    onDelete: options.onDelete,
                });
            },
        },
    ];
}
