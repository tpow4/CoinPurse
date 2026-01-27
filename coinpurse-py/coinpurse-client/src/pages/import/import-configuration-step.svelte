<script lang="ts">
    import type { Account } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import { Label } from '$lib/components/ui/label';
    import * as Card from '$lib/components/ui/card';
    import * as Select from '$lib/components/ui/select';
    import { Upload } from '@lucide/svelte';

    interface Props {
        accounts: Account[];
        accountId: number | null;
        file: File | null;
        loading: boolean;
        onAccountChange: (value: number | null) => void;
        onFileChange: (value: File | null) => void;
        onSubmit: () => void;
    }

    let { accounts, accountId, file, loading, onAccountChange, onFileChange, onSubmit }: Props =
        $props();

    let fileInput: HTMLInputElement;

    // Derived values for Select components
    const accountValue = $derived(accountId ? String(accountId) : '');

    // Get selected account for template validation
    const selectedAccount = $derived(accounts.find((a) => a.account_id === accountId));
    const hasTemplate = $derived(selectedAccount?.template_id != null);

    function handleAccountChange(value: string) {
        onAccountChange(value ? Number(value) : null);
    }

    function handleFileSelect(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            onFileChange(input.files[0]);
        }
    }

    function handleFileDrop(event: DragEvent) {
        event.preventDefault();
        if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
            onFileChange(event.dataTransfer.files[0]);
        }
    }

    function handleDragOver(event: DragEvent) {
        event.preventDefault();
    }

    function openFileDialog() {
        fileInput?.click();
    }

    const canSubmit = $derived(accountId !== null && hasTemplate && file !== null);
</script>

<Card.Root>
    <Card.Header>
        <Card.Title>Configure Import</Card.Title>
        <Card.Description>Select an account and upload your file.</Card.Description>
    </Card.Header>

    <Card.Content class="space-y-6">
        <!-- Account Selection -->
        <div class="space-y-2">
            <Label for="account-select">Account</Label>
            <Select.Root type="single" value={accountValue} onValueChange={handleAccountChange}>
                <Select.Trigger id="account-select" class="w-full">
                    {#if accountId}
                        {accounts.find((a) => a.account_id === accountId)?.account_name ??
                            'Select account'}
                    {:else}
                        Select account
                    {/if}
                </Select.Trigger>
                <Select.Content>
                    {#each accounts as account}
                        <Select.Item value={String(account.account_id)}>
                            {account.account_name}
                        </Select.Item>
                    {/each}
                </Select.Content>
            </Select.Root>
            {#if selectedAccount && !hasTemplate}
                <p class="text-destructive text-sm">
                    This account has no import template configured. Please configure a template for
                    this account before importing.
                </p>
            {/if}
        </div>

        <!-- File Upload -->
        <div class="space-y-2">
            <Label>File</Label>
            <input
                bind:this={fileInput}
                type="file"
                accept=".csv,.xlsx,.xls"
                onchange={handleFileSelect}
                class="hidden"
            />

            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div
                class="hover:bg-muted/50 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors"
                ondrop={handleFileDrop}
                ondragover={handleDragOver}
                onclick={openFileDialog}
            >
                {#if file}
                    <div class="text-center">
                        <p class="font-medium">{file.name}</p>
                        <p class="text-muted-foreground text-sm">
                            {(file.size / 1024).toFixed(1)} KB
                        </p>
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            class="mt-2"
                            onclick={(e) => {
                                e.stopPropagation();
                                onFileChange(null);
                            }}
                        >
                            Remove
                        </Button>
                    </div>
                {:else}
                    <Upload class="text-muted-foreground mb-4 size-10" />
                    <p class="mb-1 font-medium">Drop your file here or click to browse</p>
                    <p class="text-muted-foreground text-sm">Accepts CSV and Excel files</p>
                {/if}
            </div>
        </div>
    </Card.Content>

    <Card.Footer>
        <Button
            type="button"
            onclick={onSubmit}
            disabled={!canSubmit || loading}
            class="w-full"
        >
            {#if loading}
                Uploading...
            {:else}
                Upload and Preview
            {/if}
        </Button>
    </Card.Footer>
</Card.Root>
