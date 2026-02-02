<script lang="ts">
    import type { ParsedTransaction, Category } from '$lib/types';
    import { Combobox } from '$lib/components/ui/combobox';
    import { Button } from '$lib/components/ui/button';
    import * as Card from '$lib/components/ui/card';
    import * as Table from '$lib/components/ui/table';

    interface Props {
        transactions: ParsedTransaction[];
        categories: Category[];
        categoryOverrides: Map<number, number>;
        totalSelectedCount: number;
        loading: boolean;
        onOverrideChange: (overrides: Map<number, number>) => void;
        onConfirm: () => void;
        onBack: () => void;
    }

    let {
        transactions,
        categories,
        categoryOverrides,
        totalSelectedCount,
        loading,
        onOverrideChange,
        onConfirm,
        onBack,
    }: Props = $props();

    // Build category lookup map
    const categoryMap = $derived(
        new Map(categories.map((c) => [c.category_id, c.name]))
    );

    // Combobox items from categories
    const categoryItems = $derived(
        categories.map((c) => ({
            value: String(c.category_id),
            label: c.name,
        }))
    );

    // Local state for per-row combobox values (string for combobox binding)
    // Initialize from overrides or first candidate
    let rowValues = $state<Record<number, string>>(initRowValues());

    function initRowValues(): Record<number, string> {
        const values: Record<number, string> = {};
        // Note: this runs once at component creation. transactions/categoryOverrides
        // are available from props at that point.
        return values;
    }

    // Initialize row values on first render
    $effect(() => {
        // Only initialize if rowValues is empty (first render)
        if (Object.keys(rowValues).length > 0) return;
        const values: Record<number, string> = {};
        for (const tx of transactions) {
            if (categoryOverrides.has(tx.row_number)) {
                values[tx.row_number] = String(
                    categoryOverrides.get(tx.row_number)
                );
            } else if (tx.candidate_category_ids.length >= 1) {
                values[tx.row_number] = String(
                    tx.candidate_category_ids[0]
                );
            } else {
                values[tx.row_number] = '';
            }
        }
        rowValues = values;
    });

    // Count how many have a category selected
    const categorizedCount = $derived(
        transactions.filter(
            (t) => (rowValues[t.row_number] ?? '') !== ''
        ).length
    );

    // Propagate changes to parent whenever rowValues changes
    $effect(() => {
        const overrides = new Map<number, number>();
        for (const tx of transactions) {
            const val = rowValues[tx.row_number];
            if (val) {
                overrides.set(tx.row_number, Number(val));
            }
        }
        onOverrideChange(overrides);
    });

    function getCandidateNames(tx: ParsedTransaction): string[] {
        return tx.candidate_category_ids
            .map((id) => categoryMap.get(id))
            .filter((name): name is string => !!name);
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

<div class="space-y-6">
    <!-- Header -->
    <div>
        <h2 class="text-lg font-semibold">Review Categories</h2>
        <p class="text-muted-foreground text-sm">
            These transactions need a category assigned. You can skip any —
            they'll use defaults.
        </p>
    </div>

    <!-- Summary Card -->
    <Card.Root class="py-4">
        <Card.Content class="px-4 py-0">
            <span class="font-medium">{categorizedCount}</span>
            <span class="text-muted-foreground">
                of {transactions.length} transactions categorized
            </span>
        </Card.Content>
    </Card.Root>

    <!-- Transaction Table -->
    {#if transactions.length === 0}
        <div class="text-muted-foreground p-8 text-center">
            No transactions need category review.
        </div>
    {:else}
        <div class="max-h-[500px] overflow-auto">
            <Table.Root>
                <Table.Header>
                    <Table.Row>
                        <Table.Head class="w-[60px]">Row</Table.Head>
                        <Table.Head class="w-[100px]">Date</Table.Head>
                        <Table.Head>Description</Table.Head>
                        <Table.Head class="w-[120px] text-right"
                            >Amount</Table.Head
                        >
                        <Table.Head class="w-[120px]">Bank Category</Table.Head>
                        <Table.Head class="w-[220px]">Category</Table.Head>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {#each transactions as tx (tx.row_number)}
                        {@const candidateNames = getCandidateNames(tx)}
                        <Table.Row>
                            <Table.Cell
                                class="text-muted-foreground text-sm"
                            >
                                {tx.row_number}
                            </Table.Cell>
                            <Table.Cell class="text-sm">
                                {formatDate(tx.transaction_date)}
                            </Table.Cell>
                            <Table.Cell
                                class="max-w-[250px] truncate"
                                title={tx.description}
                            >
                                {tx.description}
                            </Table.Cell>
                            <Table.Cell class={getAmountClass(tx.amount)}>
                                {formatAmount(tx.amount)}
                            </Table.Cell>
                            <Table.Cell
                                class="text-muted-foreground text-sm"
                            >
                                {tx.category_name ?? '-'}
                            </Table.Cell>
                            <Table.Cell>
                                <div class="space-y-1">
                                    <Combobox
                                        items={categoryItems}
                                        bind:value={rowValues[tx.row_number]}
                                        placeholder="Select category..."
                                        searchPlaceholder="Search categories..."
                                    />
                                    {#if candidateNames.length >= 2}
                                        <div
                                            class="text-muted-foreground flex flex-wrap gap-1 text-xs"
                                        >
                                            <span>Candidates:</span>
                                            {#each candidateNames as name}
                                                <span
                                                    class="bg-muted rounded px-1.5 py-0.5"
                                                    >{name}</span
                                                >
                                            {/each}
                                        </div>
                                    {/if}
                                </div>
                            </Table.Cell>
                        </Table.Row>
                    {/each}
                </Table.Body>
            </Table.Root>
        </div>
    {/if}

    <!-- Actions -->
    <div class="flex items-center justify-between pt-4">
        <Button
            type="button"
            variant="outline"
            onclick={onBack}
            disabled={loading}
        >
            Back
        </Button>

        <Button type="button" onclick={onConfirm} disabled={loading}>
            {#if loading}
                Importing...
            {:else}
                Import {totalSelectedCount} Transaction{totalSelectedCount !== 1
                    ? 's'
                    : ''}
            {/if}
        </Button>
    </div>
</div>
