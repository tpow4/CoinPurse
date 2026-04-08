<script lang="ts">
    import type { TransactionWithNames } from '$lib/types';
    import type { ColumnDef } from '@tanstack/table-core';
    import {
        createSvelteTable,
        FlexRender,
    } from '$lib/components/ui/data-table';
    import {
        getCoreRowModel,
        getSortedRowModel,
        getPaginationRowModel,
        getFilteredRowModel,
        type SortingState,
        type ColumnFiltersState,
        type RowSelectionState,
        type PaginationState,
    } from '@tanstack/table-core';
    import * as Table from '$lib/components/ui/table';
    import { Button } from '$lib/components/ui/button';
    import { Checkbox } from '$lib/components/ui/checkbox';
    import ArrowUpDown from '@lucide/svelte/icons/arrow-up-down';
    import ChevronLeft from '@lucide/svelte/icons/chevron-left';
    import ChevronRight from '@lucide/svelte/icons/chevron-right';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        data: TransactionWithNames[];
        columns: ColumnDef<TransactionWithNames>[];
        onSelectionChange?: (selectedIds: Set<number>) => void;
    }

    let { data, columns, onSelectionChange }: Props = $props();

    let sorting = $state<SortingState>([
        { id: 'transaction_date', desc: true },
    ]);
    let columnFilters = $state<ColumnFiltersState>([]);
    let rowSelection = $state<RowSelectionState>({});
    let pagination = $state<PaginationState>({
        pageIndex: 0,
        pageSize: 50,
    });

    const table = createSvelteTable({
        get data() {
            return data;
        },
        get columns() {
            return columns;
        },
        state: {
            get sorting() {
                return sorting;
            },
            get columnFilters() {
                return columnFilters;
            },
            get rowSelection() {
                return rowSelection;
            },
            get pagination() {
                return pagination;
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
        onRowSelectionChange: (updater) => {
            if (typeof updater === 'function') {
                rowSelection = updater(rowSelection);
            } else {
                rowSelection = updater;
            }
        },
        onPaginationChange: (updater) => {
            if (typeof updater === 'function') {
                pagination = updater(pagination);
            } else {
                pagination = updater;
            }
        },
        enableRowSelection: true,
        getRowId: (row) => String(row.transaction_id),
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    });

    const pageRows = $derived(table.getPaginationRowModel().rows);
    const pageAllSelected = $derived(
        pageRows.length > 0 && pageRows.every((row) => row.getIsSelected())
    );
    const pageSomeSelected = $derived(
        pageRows.some((row) => row.getIsSelected()) && !pageAllSelected
    );

    function toggleCurrentPageRows(checked: boolean) {
        for (const row of pageRows) {
            row.toggleSelected(checked);
        }
    }

    $effect(() => {
        if (!onSelectionChange) return;
        rowSelection;
        const selectedIds = new Set(
            Object.entries(rowSelection)
                .filter(([, isSelected]) => isSelected)
                .map(([id]) => Number(id))
                .filter((id) => Number.isInteger(id))
        );
        onSelectionChange(selectedIds);
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
                        <Table.Head class="w-10">
                            <Checkbox
                                checked={pageAllSelected}
                                indeterminate={pageSomeSelected}
                                onCheckedChange={(checked) =>
                                    toggleCurrentPageRows(checked === true)}
                            />
                        </Table.Head>
                        {#each headerGroup.headers as header}
                            <Table.Head>
                                {#if !header.isPlaceholder}
                                    {#if header.column.getCanSort()}
                                        <Button
                                            variant="ghost"
                                            class="-ml-4"
                                            onclick={() =>
                                                header.column.toggleSorting()}
                                        >
                                            <FlexRender
                                                content={header.column.columnDef
                                                    .header}
                                                context={header.getContext()}
                                            />
                                            <ArrowUpDown class="ml-2 h-4 w-4" />
                                        </Button>
                                    {:else}
                                        <FlexRender
                                            content={header.column.columnDef
                                                .header}
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
                {#if pageRows.length}
                    {#each pageRows as row}
                        <Table.Row
                            data-state={row.getIsSelected() && 'selected'}
                            class={!row.original.is_active ? 'opacity-60' : ''}
                        >
                            <Table.Cell class="w-10">
                                <Checkbox
                                    checked={row.getIsSelected()}
                                    onCheckedChange={(checked) =>
                                        row.toggleSelected(checked === true)}
                                />
                            </Table.Cell>
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
                        <Table.Cell
                            colspan={columns.length + 1}
                            class="h-24 text-center"
                        >
                            {m.txn_table_empty()}
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
                {m.txn_table_showing({
                    start: table.getState().pagination.pageIndex *
                        table.getState().pagination.pageSize + 1,
                    end: Math.min(
                        (table.getState().pagination.pageIndex + 1) *
                            table.getState().pagination.pageSize,
                        table.getFilteredRowModel().rows.length
                    ),
                    total: table.getFilteredRowModel().rows.length
                })}
            {:else}
                {m.txn_table_no_results()}
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
                {m.txn_table_previous()}
            </Button>
            <span class="text-sm">
                {m.txn_table_page({ current: table.getState().pagination.pageIndex + 1, total: table.getPageCount() })}
            </span>
            <Button
                variant="outline"
                size="sm"
                disabled={!table.getCanNextPage()}
                onclick={() => table.nextPage()}
            >
                {m.txn_table_next()}
                <ChevronRight class="h-4 w-4" />
            </Button>
        </div>
    </div>
</div>
