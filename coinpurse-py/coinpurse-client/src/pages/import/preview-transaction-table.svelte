<script lang="ts">
    import type { ParsedTransaction } from '$lib/types';
    import * as Table from '$lib/components/ui/table';
    import { Checkbox } from '$lib/components/ui/checkbox';

    interface Props {
        transactions: ParsedTransaction[];
        selectedRows: Set<number>;
        selectable: boolean;
        showErrors?: boolean;
        onSelectionChange?: (rows: Set<number>) => void;
    }

    let {
        transactions,
        selectedRows,
        selectable,
        showErrors = false,
        onSelectionChange,
    }: Props = $props();

    // Check if all transactions are selected
    const allSelected = $derived(
        transactions.length > 0 &&
            transactions.every((t) => selectedRows.has(t.row_number))
    );

    // Check if some but not all transactions are selected
    const someSelected = $derived(
        transactions.some((t) => selectedRows.has(t.row_number)) && !allSelected
    );

    function toggleAll(checked: boolean) {
        if (!onSelectionChange) return;

        const newSelection = new Set(selectedRows);
        if (checked) {
            // Add all
            transactions.forEach((t) => newSelection.add(t.row_number));
        } else {
            // Remove all
            transactions.forEach((t) => newSelection.delete(t.row_number));
        }
        onSelectionChange(newSelection);
    }

    function toggleRow(rowNumber: number, checked: boolean) {
        if (!onSelectionChange) return;

        const newSelection = new Set(selectedRows);
        if (checked) {
            newSelection.add(rowNumber);
        } else {
            newSelection.delete(rowNumber);
        }
        onSelectionChange(newSelection);
    }

    function formatDate(dateStr: string | null): string {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString();
    }

    function formatAmount(cents: number): string {
        const dollars = cents / 100;
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(dollars);
    }

    function getAmountClass(amount: number): string {
        if (amount > 0) return 'text-right font-mono text-sm text-green-600';
        if (amount < 0) return 'text-right font-mono text-sm text-red-600';
        return 'text-right font-mono text-sm';
    }
</script>

{#if transactions.length === 0}
    <div class="text-muted-foreground p-8 text-center">
        No transactions in this section.
    </div>
{:else}
    <div class="max-h-100 overflow-auto">
        <Table.Root>
            <Table.Header>
                <Table.Row>
                    {#if selectable}
                        <Table.Head class="w-12.5">
                            <Checkbox
                                checked={allSelected}
                                indeterminate={someSelected}
                                onCheckedChange={(checked) =>
                                    toggleAll(checked === true)}
                            />
                        </Table.Head>
                    {/if}
                    <Table.Head class="w-15">Row</Table.Head>
                    <Table.Head class="w-25">Date</Table.Head>
                    <Table.Head>Description</Table.Head>
                    <Table.Head class="w-30 text-right">Amount</Table.Head>
                    <Table.Head class="w-25">Category</Table.Head>
                    {#if showErrors}
                        <Table.Head>Errors</Table.Head>
                    {/if}
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {#each transactions as tx (tx.row_number)}
                    <Table.Row>
                        {#if selectable}
                            <Table.Cell>
                                <Checkbox
                                    checked={selectedRows.has(tx.row_number)}
                                    onCheckedChange={(checked) =>
                                        toggleRow(
                                            tx.row_number,
                                            checked === true
                                        )}
                                />
                            </Table.Cell>
                        {/if}
                        <Table.Cell class="text-muted-foreground text-sm"
                            >{tx.row_number}</Table.Cell
                        >
                        <Table.Cell class="text-sm"
                            >{formatDate(tx.transaction_date)}</Table.Cell
                        >
                        <Table.Cell
                            class="max-w-75 truncate"
                            title={tx.description}
                        >
                            {tx.description}
                        </Table.Cell>
                        <Table.Cell class={getAmountClass(tx.amount)}>
                            {formatAmount(tx.amount)}
                        </Table.Cell>
                        <Table.Cell class="text-muted-foreground text-sm">
                            {tx.category_name ?? '-'}
                        </Table.Cell>
                        {#if showErrors}
                            <Table.Cell class="text-sm text-red-600">
                                {tx.validation_errors.join(', ')}
                            </Table.Cell>
                        {/if}
                    </Table.Row>
                {/each}
            </Table.Body>
        </Table.Root>
    </div>
{/if}
