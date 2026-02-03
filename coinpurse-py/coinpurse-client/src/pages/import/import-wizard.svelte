<script lang="ts">
    import type {
        Account,
        Category,
        ImportConfirmResponse,
        ImportPreviewResponse,
    } from '$lib/types';
    import { accountsApi } from '$lib/api/accounts';
    import { categoriesApi } from '$lib/api/categories';
    import { importApi } from '$lib/api/import';
    import ImportConfigurationStep from './import-configuration-step.svelte';
    import ImportPreviewStep from './import-preview-step.svelte';
    import ImportCategorizeStep from './import-categorize-step.svelte';
    import ImportResultStep from './import-result-step.svelte';

    // Wizard state
    type WizardStep = 'config' | 'preview' | 'categorize' | 'result';
    let currentStep = $state<WizardStep>('config');

    // Step 1: Configuration state
    let accountId = $state<number | null>(null);
    let file = $state<File | null>(null);

    // Step 2: Preview state
    let previewResponse = $state<ImportPreviewResponse | null>(null);
    let selectedRows = $state<Set<number>>(new Set());

    // Step 3: Categorize state
    let categoryOverrides = $state<Map<number, number>>(new Map());

    // Step 4: Result state
    let confirmResponse = $state<ImportConfirmResponse | null>(null);

    // UI state
    let loading = $state(false);
    let error = $state('');

    // Reference data
    let accounts = $state<Account[]>([]);
    let categories = $state<Category[]>([]);

    // Load reference data on mount
    async function loadReferenceData() {
        try {
            const [accountsRes, categoriesRes] = await Promise.all([
                accountsApi.getAll(false),
                categoriesApi.getAll(false),
            ]);
            // Only show accounts that track transactions
            accounts = accountsRes.filter((a) => a.tracks_transactions);
            categories = categoriesRes;
        } catch (e) {
            console.error('Failed to load reference data:', e);
            error = 'Failed to load reference data';
        }
    }

    $effect(() => {
        loadReferenceData();
    });

    // Handle account selection
    function handleAccountChange(newAccountId: number | null) {
        accountId = newAccountId;
    }

    // Handle file upload and preview
    async function handleUploadAndPreview() {
        if (!accountId || !file) {
            error = 'Please select an account and file';
            return;
        }

        loading = true;
        error = '';

        try {
            previewResponse = await importApi.uploadAndPreview(file, accountId);

            // Pre-select all valid, non-duplicate rows
            selectedRows = new Set(
                previewResponse.transactions
                    .filter(
                        (t) =>
                            !t.is_duplicate && t.validation_errors.length === 0
                    )
                    .map((t) => t.row_number)
            );

            currentStep = 'preview';
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to upload file';
        } finally {
            loading = false;
        }
    }

    // Compute flagged transactions that need category attention
    function getFlaggedTransactions() {
        if (!previewResponse) return [];
        return previewResponse.transactions.filter(
            (t) =>
                selectedRows.has(t.row_number) &&
                (t.candidate_category_ids.length === 0 ||
                    t.candidate_category_ids.length >= 2)
        );
    }

    // Handle proceeding from preview to categorize (or skip to confirm)
    function handleProceedToCategorize() {
        const flagged = getFlaggedTransactions();
        if (flagged.length === 0) {
            // All selected transactions are cleanly categorized — skip to confirm
            handleConfirmImport();
        } else {
            currentStep = 'categorize';
        }
    }

    // Handle confirm import
    async function handleConfirmImport() {
        if (!previewResponse || selectedRows.size === 0) {
            error = 'No rows selected for import';
            return;
        }

        loading = true;
        error = '';

        try {
            // Build category_overrides from the Map
            const overrides: Record<number, number> = {};
            categoryOverrides.forEach((categoryId, rowNumber) => {
                if (selectedRows.has(rowNumber)) {
                    overrides[rowNumber] = categoryId;
                }
            });

            confirmResponse = await importApi.confirmImport({
                import_batch_id: previewResponse.import_batch_id,
                selected_rows: Array.from(selectedRows),
                ...(Object.keys(overrides).length > 0
                    ? { category_overrides: overrides }
                    : {}),
            });

            currentStep = 'result';
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to confirm import';
        } finally {
            loading = false;
        }
    }

    // Reset wizard
    function handleReset() {
        currentStep = 'config';
        accountId = null;
        file = null;
        previewResponse = null;
        selectedRows = new Set();
        categoryOverrides = new Map();
        confirmResponse = null;
        error = '';
    }

    // Go back to configuration
    function handleBackToConfig() {
        currentStep = 'config';
        previewResponse = null;
        selectedRows = new Set();
        categoryOverrides = new Map();
        error = '';
    }

    // Go back to preview from categorize
    function handleBackToPreview() {
        currentStep = 'preview';
        error = '';
    }

    function handleCategoryOverridesChange(overrides: Map<number, number>) {
        categoryOverrides = overrides;
    }

    // Flagged transactions for the categorize step (derived)
    const flaggedTransactions = $derived(getFlaggedTransactions());
</script>

<!-- Step indicator -->
<div class="mb-8">
    <div class="flex items-center justify-center gap-4">
        <div
            class="flex items-center gap-2"
            class:text-primary={currentStep === 'config'}
            class:text-muted-foreground={currentStep !== 'config'}
        >
            <div
                class="flex size-8 items-center justify-center rounded-full border-2"
                class:border-primary={currentStep === 'config'}
                class:bg-primary={currentStep === 'config'}
                class:text-primary-foreground={currentStep === 'config'}
            >
                1
            </div>
            <span class="font-medium">Configure</span>
        </div>

        <div class="h-px w-12 bg-border"></div>

        <div
            class="flex items-center gap-2"
            class:text-primary={currentStep === 'preview'}
            class:text-muted-foreground={currentStep !== 'preview'}
        >
            <div
                class="flex size-8 items-center justify-center rounded-full border-2"
                class:border-primary={currentStep === 'preview'}
                class:bg-primary={currentStep === 'preview'}
                class:text-primary-foreground={currentStep === 'preview'}
            >
                2
            </div>
            <span class="font-medium">Preview</span>
        </div>

        <div class="h-px w-12 bg-border"></div>

        <div
            class="flex items-center gap-2"
            class:text-primary={currentStep === 'categorize'}
            class:text-muted-foreground={currentStep !== 'categorize'}
        >
            <div
                class="flex size-8 items-center justify-center rounded-full border-2"
                class:border-primary={currentStep === 'categorize'}
                class:bg-primary={currentStep === 'categorize'}
                class:text-primary-foreground={currentStep === 'categorize'}
            >
                3
            </div>
            <span class="font-medium">Categorize</span>
        </div>

        <div class="h-px w-12 bg-border"></div>

        <div
            class="flex items-center gap-2"
            class:text-primary={currentStep === 'result'}
            class:text-muted-foreground={currentStep !== 'result'}
        >
            <div
                class="flex size-8 items-center justify-center rounded-full border-2"
                class:border-primary={currentStep === 'result'}
                class:bg-primary={currentStep === 'result'}
                class:text-primary-foreground={currentStep === 'result'}
            >
                4
            </div>
            <span class="font-medium">Result</span>
        </div>
    </div>
</div>

<!-- Error display -->
{#if error}
    <div class="bg-destructive/10 text-destructive mb-4 rounded-md p-4">
        {error}
    </div>
{/if}

<!-- Step content -->
{#if currentStep === 'config'}
    <ImportConfigurationStep
        {accounts}
        {accountId}
        {file}
        {loading}
        onAccountChange={handleAccountChange}
        onFileChange={(v) => (file = v)}
        onSubmit={handleUploadAndPreview}
    />
{:else if currentStep === 'preview' && previewResponse}
    <ImportPreviewStep
        {previewResponse}
        {selectedRows}
        {loading}
        onSelectionChange={(rows) => (selectedRows = rows)}
        onConfirm={handleProceedToCategorize}
        onBack={handleBackToConfig}
    />
{:else if currentStep === 'categorize' && previewResponse}
    <ImportCategorizeStep
        transactions={flaggedTransactions}
        {categories}
        {categoryOverrides}
        totalSelectedCount={selectedRows.size}
        {loading}
        onOverrideChange={handleCategoryOverridesChange}
        onConfirm={handleConfirmImport}
        onBack={handleBackToPreview}
    />
{:else if currentStep === 'result' && confirmResponse}
    <ImportResultStep {confirmResponse} onImportAnother={handleReset} />
{/if}
