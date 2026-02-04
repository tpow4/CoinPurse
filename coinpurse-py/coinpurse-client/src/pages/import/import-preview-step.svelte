<script lang="ts">
    import type { ImportPreviewResponse } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import * as Card from '$lib/components/ui/card';
    import PreviewSummaryCards from './preview-summary-cards.svelte';
    import PreviewTransactionSection from './preview-transaction-section.svelte';
    import PreviewTransactionTable from './preview-transaction-table.svelte';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        previewResponse: ImportPreviewResponse;
        selectedRows: Set<number>;
        loading: boolean;
        onSelectionChange: (rows: Set<number>) => void;
        onConfirm: () => void;
        onBack: () => void;
    }

    let {
        previewResponse,
        selectedRows,
        loading,
        onSelectionChange,
        onConfirm,
        onBack,
    }: Props = $props();

    // Categorize transactions
    const validTransactions = $derived(
        previewResponse.transactions.filter(
            (t) => !t.is_duplicate && t.validation_errors.length === 0
        )
    );

    const duplicateTransactions = $derived(
        previewResponse.transactions.filter((t) => t.is_duplicate)
    );

    const errorTransactions = $derived(
        previewResponse.transactions.filter(
            (t) => !t.is_duplicate && t.validation_errors.length > 0
        )
    );

    // Count selected duplicates for warning display
    const selectedDuplicateCount = $derived(
        duplicateTransactions.filter((t) => selectedRows.has(t.row_number))
            .length
    );

    const totalSelected = $derived(selectedRows.size);

    // Handle selection changes for valid transactions
    function handleValidSelectionChange(rows: Set<number>) {
        // Keep duplicate selections intact, update only valid selections
        const newSelection = new Set<number>();

        // Add duplicate selections that were already selected
        duplicateTransactions.forEach((t) => {
            if (selectedRows.has(t.row_number)) {
                newSelection.add(t.row_number);
            }
        });

        // Add the new valid selections
        validTransactions.forEach((t) => {
            if (rows.has(t.row_number)) {
                newSelection.add(t.row_number);
            }
        });

        onSelectionChange(newSelection);
    }

    // Handle selection changes for duplicate transactions
    function handleDuplicateSelectionChange(rows: Set<number>) {
        // Keep valid selections intact, update only duplicate selections
        const newSelection = new Set<number>();

        // Add valid selections that were already selected
        validTransactions.forEach((t) => {
            if (selectedRows.has(t.row_number)) {
                newSelection.add(t.row_number);
            }
        });

        // Add the new duplicate selections
        duplicateTransactions.forEach((t) => {
            if (rows.has(t.row_number)) {
                newSelection.add(t.row_number);
            }
        });

        onSelectionChange(newSelection);
    }
</script>

<div class="space-y-6">
    <!-- Summary Cards -->
    <PreviewSummaryCards summary={previewResponse.summary} />

    <!-- Selection Summary -->
    <Card.Root class="py-4">
        <Card.Content class="flex items-center justify-between px-4 py-0">
            <div>
                <span class="text-muted-foreground">
                    {m.imp_preview_selected({ count: totalSelected })}</span
                >
                {#if selectedDuplicateCount > 0}
                    <span class="ml-2 text-amber-600">
                        {m.imp_preview_includes_duplicates({ count: selectedDuplicateCount, suffix: selectedDuplicateCount !== 1 ? 's' : '' })}
                    </span>
                {/if}
            </div>
        </Card.Content>
    </Card.Root>

    <!-- Valid Transactions -->
    {#if validTransactions.length > 0}
        <PreviewTransactionSection
            title={m.imp_preview_valid()}
            count={validTransactions.length}
            variant="default"
            defaultOpen={true}
        >
            <PreviewTransactionTable
                transactions={validTransactions}
                {selectedRows}
                selectable={true}
                onSelectionChange={handleValidSelectionChange}
            />
        </PreviewTransactionSection>
    {/if}

    <!-- Duplicate Transactions -->
    {#if duplicateTransactions.length > 0}
        <PreviewTransactionSection
            title={m.imp_preview_duplicate()}
            count={duplicateTransactions.length}
            variant="warning"
            defaultOpen={true}
        >
            <div class="bg-amber-500/10 p-3 text-sm text-amber-700">
                {m.imp_preview_duplicate_warning()}
            </div>
            <PreviewTransactionTable
                transactions={duplicateTransactions}
                {selectedRows}
                selectable={true}
                onSelectionChange={handleDuplicateSelectionChange}
            />
        </PreviewTransactionSection>
    {/if}

    <!-- Error Transactions -->
    {#if errorTransactions.length > 0}
        <PreviewTransactionSection
            title={m.imp_preview_validation_errors()}
            count={errorTransactions.length}
            variant="error"
            defaultOpen={errorTransactions.length <= 10}
        >
            <div class="bg-red-500/10 p-3 text-sm text-red-700">
                {m.imp_preview_validation_warning()}
            </div>
            <PreviewTransactionTable
                transactions={errorTransactions}
                {selectedRows}
                selectable={false}
                showErrors={true}
            />
        </PreviewTransactionSection>
    {/if}

    <!-- Actions -->
    <div class="flex items-center justify-between pt-4">
        <Button
            type="button"
            variant="outline"
            onclick={onBack}
            disabled={loading}>{m.imp_btn_back()}</Button
        >

        <Button
            type="button"
            onclick={onConfirm}
            disabled={loading || totalSelected === 0}
        >
            {m.imp_btn_next_categories()}
        </Button>
    </div>
</div>
