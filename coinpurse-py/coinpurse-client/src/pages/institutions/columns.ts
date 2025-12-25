import type { ColumnDef } from "@tanstack/table-core";
import type { Institution } from "$lib/types";
import { renderComponent } from "$lib/components/ui/data-table/render-helpers.js";
import InstitutionsTableActions from "./institutions-table-actions.svelte";

interface ColumnsOptions {
	onEdit: (institution: Institution) => void;
	onDelete: (institution: Institution) => void;
}

export function createColumns(options: ColumnsOptions): ColumnDef<Institution>[] {
	return [
		{
			accessorKey: "name",
			header: "Name",
		},
		{
			accessorKey: "is_active",
			header: "Status",
			cell: ({ row }) => {
				const isActive = row.getValue("is_active") as boolean;
				return isActive ? "Active" : "Inactive";
			},
		},
		{
			accessorKey: "created_at",
			header: "Created",
			cell: ({ row }) => {
				const date = new Date(row.getValue("created_at") as string);
				return date.toLocaleDateString();
			},
		},
		{
			id: "actions",
			header: "Actions",
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
