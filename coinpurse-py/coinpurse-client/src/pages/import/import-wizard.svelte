<script lang="ts">
    import type {
        Account,
        ImportConfirmResponse,
        ImportPreviewResponse,
        ImportTemplate,
    } from '$lib/types';
    import { accountsApi } from '$lib/api/accounts';
    import { importApi } from '$lib/api/import';
    import ImportConfigurationStep from './import-configuration-step.svelte';
    import ImportPreviewStep from './import-preview-step.svelte';
    import ImportResultStep from './import-result-step.svelte';

    // Wizard state
    type WizardStep = 'config' | 'preview' | 'result';
    let currentStep = $state<WizardStep>('config');

    // Step 1: Configuration state
    let accountId = $state<number | null>(null);
    let templateId = $state<number | null>(null);
    let file = $state<File | null>(null);

    // Step 2: Preview state
    let previewResponse = $state<ImportPreviewResponse | null>(null);
    let selectedRows = $state<Set<number>>(new Set());

    // Step 3: Result state
    let confirmResponse = $state<ImportConfirmResponse | null>(null);

    // UI state
    let loading = $state(false);
    let error = $state('');

    // Reference data
    let accounts = $state<Account[]>([]);
    let templates = $state<ImportTemplate[]>([]);

    // Load reference data on mount
    async function loadReferenceData() {
        try {
            const [accountsRes, templatesRes] = await Promise.all([
                accountsApi.getAll(false),
                importApi.getTemplates(false),
            ]);
            // Only show accounts that track transactions
            accounts = accountsRes.filter((a) => a.tracks_transactions);
            templates = templatesRes;
        } catch (e) {
            console.error('Failed to load reference data:', e);
            error = 'Failed to load accounts and templates';
        }
    }

    $effect(() => {
        loadReferenceData();
    });

    // Handle account selection - auto-populate template
    function handleAccountChange(newAccountId: number | null) {
        accountId = newAccountId;
        if (newAccountId) {
            const account = accounts.find((a) => a.account_id === newAccountId);
            if (account?.template_id) {
                templateId = account.template_id;
            }
        }
    }

    // Handle file upload and preview
    async function handleUploadAndPreview() {
        if (!accountId || !templateId || !file) {
            error = 'Please select an account, template, and file';
            return;
        }

        loading = true;
        error = '';

        try {
            previewResponse = await importApi.uploadAndPreview(
                file,
                accountId,
                templateId
            );

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

    // Handle confirm import
    async function handleConfirmImport() {
        if (!previewResponse || selectedRows.size === 0) {
            error = 'No rows selected for import';
            return;
        }

        loading = true;
        error = '';

        try {
            confirmResponse = await importApi.confirmImport({
                import_batch_id: previewResponse.import_batch_id,
                selected_rows: Array.from(selectedRows),
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
        templateId = null;
        file = null;
        previewResponse = null;
        selectedRows = new Set();
        confirmResponse = null;
        error = '';
    }

    // Go back to configuration
    function handleBackToConfig() {
        currentStep = 'config';
        previewResponse = null;
        selectedRows = new Set();
        error = '';
    }
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
            class:text-primary={currentStep === 'result'}
            class:text-muted-foreground={currentStep !== 'result'}
        >
            <div
                class="flex size-8 items-center justify-center rounded-full border-2"
                class:border-primary={currentStep === 'result'}
                class:bg-primary={currentStep === 'result'}
                class:text-primary-foreground={currentStep === 'result'}
            >
                3
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
        {templates}
        {accountId}
        {templateId}
        {file}
        {loading}
        onAccountChange={handleAccountChange}
        onTemplateChange={(v) => (templateId = v)}
        onFileChange={(v) => (file = v)}
        onSubmit={handleUploadAndPreview}
    />
{:else if currentStep === 'preview' && previewResponse}
    <ImportPreviewStep
        {previewResponse}
        {selectedRows}
        {loading}
        onSelectionChange={(rows) => (selectedRows = rows)}
        onConfirm={handleConfirmImport}
        onBack={handleBackToConfig}
    />
{:else if currentStep === 'result' && confirmResponse}
    <ImportResultStep {confirmResponse} onImportAnother={handleReset} />
{/if}
