import type { ColumnDef } from '@tanstack/table-core';
import type { Category } from '$lib/types';
import { renderComponent } from '$lib/components/ui/data-table/render-helpers.js';
import CategoriesTableActions from './categories-table-actions.svelte';

interface ColumnsOptions {
    onEdit: (category: Category) => void;
    onDelete: (category: Category) => void;
}

export function createColumns(options: ColumnsOptions): ColumnDef<Category>[] {
    return [
        {
            accessorKey: 'name',
            header: 'Name',
        },
        {
            accessorKey: 'is_active',
            header: 'Status',
            cell: ({ row }) => {
                const isActive = row.getValue('is_active') as boolean;
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
                return renderComponent(CategoriesTableActions, {
                    category: row.original,
                    onEdit: options.onEdit,
                    onDelete: options.onDelete,
                });
            },
        },
    ];
}
