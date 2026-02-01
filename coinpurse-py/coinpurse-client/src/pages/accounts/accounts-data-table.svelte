<script lang="ts">
    import type { AccountWithInstitution } from './columns';
    import type { ColumnDef } from '@tanstack/table-core';
    import {
        createSvelteTable,
        FlexRender,
    } from '$lib/components/ui/data-table';
    import { getCoreRowModel } from '@tanstack/table-core';
    import * as Table from '$lib/components/ui/table';

    interface Props {
        data: AccountWithInstitution[];
        columns: ColumnDef<AccountWithInstitution>[];
    }

    let { data, columns }: Props = $props();

    const table = createSvelteTable({
        get data() {
            return data;
        },
        get columns() {
            return columns;
        },
        initialState: {
            columnPinning: {
                right: ['actions'],
            },
        },
        getCoreRowModel: getCoreRowModel(),
    });
</script>

<div class="rounded-md border">
    <Table.Root>
        <Table.Header>
            {#each table.getHeaderGroups() as headerGroup}
                <Table.Row>
                    {#each headerGroup.headers as header}
                        <Table.Head>
                            {#if !header.isPlaceholder}
                                <FlexRender
                                    content={header.column.columnDef.header}
                                    context={header.getContext()}
                                />
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
                        class={!row.original.active ? 'opacity-60' : ''}
                    >
                        {#each row.getVisibleCells() as cell}
                            <Table.Cell
                                class={cell.column.id === 'actions'
                                    ? 'text-right'
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
                        colspan={columns.length}
                        class="h-24 text-center"
                    >
                        No results.
                    </Table.Cell>
                </Table.Row>
            {/if}
        </Table.Body>
    </Table.Root>
</div>
