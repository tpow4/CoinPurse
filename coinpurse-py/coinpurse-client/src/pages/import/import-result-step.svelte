<script lang="ts">
	import type { ImportConfirmResponse } from '$lib/types';
	import { ImportStatus } from '$lib/types';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { CheckCircle, XCircle, Upload, ArrowRight } from '@lucide/svelte';

	interface Props {
		confirmResponse: ImportConfirmResponse;
		onImportAnother: () => void;
	}

	let { confirmResponse, onImportAnother }: Props = $props();

	const isSuccess = $derived(confirmResponse.status === ImportStatus.COMPLETED);
</script>

<Card.Root class="mx-auto max-w-md">
	<Card.Header class="text-center">
		{#if isSuccess}
			<div class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-green-500/10">
				<CheckCircle class="size-8 text-green-500" />
			</div>
			<Card.Title class="text-2xl">Import Successful</Card.Title>
			<Card.Description>Your transactions have been imported.</Card.Description>
		{:else}
			<div class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-red-500/10">
				<XCircle class="size-8 text-red-500" />
			</div>
			<Card.Title class="text-2xl">Import Failed</Card.Title>
			<Card.Description>There was a problem importing your transactions.</Card.Description>
		{/if}
	</Card.Header>

	<Card.Content>
		<div class="space-y-3 rounded-lg border p-4">
			<div class="flex justify-between">
				<span class="text-muted-foreground">Imported</span>
				<span class="font-medium text-green-600">{confirmResponse.imported_count}</span>
			</div>
			<div class="flex justify-between">
				<span class="text-muted-foreground">Skipped</span>
				<span class="font-medium">{confirmResponse.skipped_count}</span>
			</div>
			{#if confirmResponse.duplicate_count > 0}
				<div class="flex justify-between">
					<span class="text-muted-foreground">Duplicates Imported</span>
					<span class="font-medium text-amber-600">{confirmResponse.duplicate_count}</span>
				</div>
			{/if}
		</div>
	</Card.Content>

	<Card.Footer class="flex flex-col gap-3">
		<Button type="button" variant="outline" onclick={onImportAnother} class="w-full">
			<Upload class="mr-2 size-4" />
			Import Another File
		</Button>
		<Button href="/transactions" class="w-full">
			<span>View Transactions</span>
			<ArrowRight class="ml-2 size-4" />
		</Button>
	</Card.Footer>
</Card.Root>
