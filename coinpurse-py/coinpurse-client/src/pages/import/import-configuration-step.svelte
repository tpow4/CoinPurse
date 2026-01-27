<script lang="ts">
	import type { Account, ImportTemplate } from '$lib/types';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import * as Card from '$lib/components/ui/card';
	import * as Select from '$lib/components/ui/select';
	import { Upload } from '@lucide/svelte';

	interface Props {
		accounts: Account[];
		templates: ImportTemplate[];
		accountId: number | null;
		templateId: number | null;
		file: File | null;
		loading: boolean;
		onAccountChange: (value: number | null) => void;
		onTemplateChange: (value: number | null) => void;
		onFileChange: (value: File | null) => void;
		onSubmit: () => void;
	}

	let {
		accounts,
		templates,
		accountId,
		templateId,
		file,
		loading,
		onAccountChange,
		onTemplateChange,
		onFileChange,
		onSubmit,
	}: Props = $props();

	// Local state for select bindings
	let localAccountId = $state<string>('');
	let localTemplateId = $state<string>('');
	let fileInput: HTMLInputElement;

	// Sync local state with props
	$effect(() => {
		localAccountId = accountId ? String(accountId) : '';
	});
	$effect(() => {
		localTemplateId = templateId ? String(templateId) : '';
	});

	// Notify parent when local values change
	$effect(() => {
		const numericValue = localAccountId ? Number(localAccountId) : null;
		if (numericValue !== accountId) {
			onAccountChange(numericValue);
		}
	});
	$effect(() => {
		const numericValue = localTemplateId ? Number(localTemplateId) : null;
		if (numericValue !== templateId) {
			onTemplateChange(numericValue);
		}
	});

	// Get selected template for file type info
	const selectedTemplate = $derived(templates.find((t) => t.template_id === templateId));

	// Get file extension hint from template
	const acceptedFileTypes = $derived(() => {
		if (!selectedTemplate) return '.csv,.xlsx,.xls';
		return selectedTemplate.file_format === 'excel' ? '.xlsx,.xls' : '.csv';
	});

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

	const canSubmit = $derived(accountId !== null && templateId !== null && file !== null);
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Configure Import</Card.Title>
		<Card.Description>Select an account and template, then upload your file.</Card.Description>
	</Card.Header>

	<Card.Content class="space-y-6">
		<!-- Account Selection -->
		<div class="space-y-2">
			<Label for="account-select">Account</Label>
			<Select.Root type="single" bind:value={localAccountId}>
				<Select.Trigger id="account-select" class="w-full">
					{#if localAccountId}
						{accounts.find((a) => String(a.account_id) === localAccountId)?.account_name ??
							'Select account'}
					{:else}
						Select account
					{/if}
				</Select.Trigger>
				<Select.Content>
					{#each accounts as account}
						<Select.Item value={String(account.account_id)} label={account.account_name} />
					{/each}
				</Select.Content>
			</Select.Root>
			{#if accountId && accounts.find((a) => a.account_id === accountId)?.template_id}
				<p class="text-muted-foreground text-sm">
					This account has an associated template that will be auto-selected.
				</p>
			{/if}
		</div>

		<!-- Template Selection -->
		<div class="space-y-2">
			<Label for="template-select">Import Template</Label>
			<Select.Root type="single" bind:value={localTemplateId}>
				<Select.Trigger id="template-select" class="w-full">
					{#if localTemplateId}
						{templates.find((t) => String(t.template_id) === localTemplateId)?.template_name ??
							'Select template'}
					{:else}
						Select template
					{/if}
				</Select.Trigger>
				<Select.Content>
					{#each templates as template}
						<Select.Item value={String(template.template_id)} label={template.template_name} />
					{/each}
				</Select.Content>
			</Select.Root>
			{#if selectedTemplate}
				<p class="text-muted-foreground text-sm">
					Expects: {selectedTemplate.file_format.toUpperCase()} file
				</p>
			{/if}
		</div>

		<!-- File Upload -->
		<div class="space-y-2">
			<Label>File</Label>
			<input
				bind:this={fileInput}
				type="file"
				accept={acceptedFileTypes()}
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
					<p class="text-muted-foreground text-sm">
						{#if selectedTemplate}
							Accepts {selectedTemplate.file_format.toUpperCase()} files
						{:else}
							Select a template first to see accepted file types
						{/if}
					</p>
				{/if}
			</div>
		</div>
	</Card.Content>

	<Card.Footer>
		<Button type="button" onclick={onSubmit} disabled={!canSubmit || loading} class="w-full">
			{#if loading}
				Uploading...
			{:else}
				Upload and Preview
			{/if}
		</Button>
	</Card.Footer>
</Card.Root>
