<script lang="ts">
	import type { TransactionWithNames } from '$lib/types';
	import type { ColumnDef } from '@tanstack/table-core';
	import { createSvelteTable, FlexRender } from '$lib/components/ui/data-table';
	import {
		getCoreRowModel,
		getSortedRowModel,
		getPaginationRowModel,
		getFilteredRowModel,
		type SortingState,
		type ColumnFiltersState,
	} from '@tanstack/table-core';
	import * as Table from '$lib/components/ui/table';
	import { Button } from '$lib/components/ui/button';
	import ArrowUpDown from '@lucide/svelte/icons/arrow-up-down';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';

	interface Props {
		data: TransactionWithNames[];
		columns: ColumnDef<TransactionWithNames>[];
	}

	let { data, columns }: Props = $props();

	let sorting = $state<SortingState>([{ id: 'transaction_date', desc: true }]);
	let columnFilters = $state<ColumnFiltersState>([]);

	const table = createSvelteTable({
		get data() {
			return data;
		},
		columns,
		state: {
			get sorting() {
				return sorting;
			},
			get columnFilters() {
				return columnFilters;
			},
		},
		onSortingChange: (updater) => {
			if (typeof updater === 'function') {
				sorting = updater(sorting);
			} else {
				sorting = updater;
			}
		},
		onColumnFiltersChange: (updater) => {
			if (typeof updater === 'function') {
				columnFilters = updater(columnFilters);
			} else {
				columnFilters = updater;
			}
		},
		getCoreRowModel: getCoreRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		initialState: {
			pagination: { pageSize: 50 },
		},
	});

	// Expose table for parent components to set filters
	export function getTable() {
		return table;
	}
</script>

<div class="space-y-4">
	<div class="rounded-md border">
		<Table.Root>
			<Table.Header>
				{#each table.getHeaderGroups() as headerGroup}
					<Table.Row>
						{#each headerGroup.headers as header}
							<Table.Head>
								{#if !header.isPlaceholder}
									{#if header.column.getCanSort()}
										<Button
											variant="ghost"
											class="-ml-4"
											onclick={() => header.column.toggleSorting()}
										>
											<FlexRender
												content={header.column.columnDef.header}
												context={header.getContext()}
											/>
											<ArrowUpDown class="ml-2 h-4 w-4" />
										</Button>
									{:else}
										<FlexRender
											content={header.column.columnDef.header}
											context={header.getContext()}
										/>
									{/if}
								{/if}
							</Table.Head>
						{/each}
					</Table.Row>
				{/each}
			</Table.Header>
			<Table.Body>
				{#if table.getRowModel().rows?.length}
					{#each table.getRowModel().rows as row}
						<Table.Row
							data-state={row.getIsSelected() && 'selected'}
							class={!row.original.is_active ? 'opacity-60' : ''}
						>
							{#each row.getVisibleCells() as cell}
								<Table.Cell
									class={cell.column.id === 'amount'
										? row.original.amount < 0
											? 'text-red-600'
											: 'text-green-600'
										: ''}
								>
									<FlexRender
										content={cell.column.columnDef.cell}
										context={cell.getContext()}
									/>
								</Table.Cell>
							{/each}
						</Table.Row>
					{/each}
				{:else}
					<Table.Row>
						<Table.Cell colspan={columns.length} class="h-24 text-center">
							No transactions found.
						</Table.Cell>
					</Table.Row>
				{/if}
			</Table.Body>
		</Table.Root>
	</div>

	<!-- Pagination -->
	<div class="flex items-center justify-between">
		<span class="text-sm text-gray-600">
			{#if table.getFilteredRowModel().rows.length > 0}
				Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}–{Math.min(
					(table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
					table.getFilteredRowModel().rows.length
				)} of {table.getFilteredRowModel().rows.length}
			{:else}
				No results
			{/if}
		</span>

		<div class="flex items-center gap-2">
			<Button
				variant="outline"
				size="sm"
				disabled={!table.getCanPreviousPage()}
				onclick={() => table.previousPage()}
			>
				<ChevronLeft class="h-4 w-4" />
				Previous
			</Button>
			<span class="text-sm">
				Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
			</span>
			<Button
				variant="outline"
				size="sm"
				disabled={!table.getCanNextPage()}
				onclick={() => table.nextPage()}
			>
				Next
				<ChevronRight class="h-4 w-4" />
			</Button>
		</div>
	</div>
</div>
