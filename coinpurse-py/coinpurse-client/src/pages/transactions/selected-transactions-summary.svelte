<script lang="ts">
	import { formatCentsCurrency } from '$lib/format';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import * as m from '$lib/paraglide/messages';

	interface Props {
		selectedCount: number;
		filteredCount: number;
		totalCents: number;
		showSelection: boolean;
	}

	let { selectedCount, filteredCount, totalCents, showSelection }: Props = $props();

	const totalClass = $derived(
		totalCents < 0
			? 'text-red-600'
			: totalCents > 0
				? 'text-green-600'
				: 'text-foreground'
	);
</script>

<Card>
	<CardHeader class="pb-2">
		<CardTitle>{showSelection ? m.txn_selected_total() : m.txn_total()}</CardTitle>
	</CardHeader>
	<CardContent>
		<div class="flex flex-wrap items-end justify-between gap-4">
			<div class="space-y-1">
				{#if showSelection}
					<p class="text-muted-foreground text-sm">
						{m.txn_selected_count({ count: selectedCount })}
					</p>
				{:else}
					<p class="text-muted-foreground text-sm">
						{m.txn_total_count({ count: filteredCount })}
					</p>
				{/if}
				<p class={`text-2xl font-semibold ${totalClass}`}>
					{formatCentsCurrency(totalCents)}
				</p>
				{#if showSelection}
					<p class="text-muted-foreground text-xs">
						{m.txn_selected_hint_pages()}
					</p>
				{:else}
					<p class="text-muted-foreground text-xs">
						{m.txn_total_hint_filtered()}
					</p>
				{/if}
			</div>
		</div>
	</CardContent>
</Card>
