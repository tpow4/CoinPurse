<script lang="ts">
	import { PieChart } from 'layerchart';
	import * as Chart from '$lib/components/ui/chart';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import * as m from '$lib/paraglide/messages';

	export interface BreakdownDatum {
		key: string;
		label: string;
		value: number;
		color: string;
	}

	interface Props {
		accountData: BreakdownDatum[];
		categoryData: BreakdownDatum[];
		type: 'credits' | 'debits';
	}

	let { accountData, categoryData, type }: Props = $props();

	function createChartConfig(data: BreakdownDatum[]): Chart.ChartConfig {
		return data.reduce((config, item) => {
			config[item.key] = {
				label: item.label,
				color: item.color,
			};
			return config;
		}, {} as Chart.ChartConfig);
	}

	const accountConfig = $derived(createChartConfig(accountData));
	const categoryConfig = $derived(createChartConfig(categoryData));

	const hasAccountData = $derived(accountData.length > 0);
	const hasCategoryData = $derived(categoryData.length > 0);
	const accountMaxValue = $derived(
		accountData.reduce((sum, item) => sum + item.value, 0)
	);
	const categoryMaxValue = $derived(
		categoryData.reduce((sum, item) => sum + item.value, 0)
	);
	const accountTitle = $derived(
		type === 'credits' ? 'Credits by Account' : m.txn_chart_by_account()
	);
	const categoryTitle = $derived(
		type === 'credits' ? 'Credits by Category' : m.txn_chart_by_category()
	);
	const emptyMessage = $derived(
		type === 'credits'
			? 'No credit transactions in the current filtered results.'
			: m.txn_chart_empty()
	);
	const hintMessage = $derived(
		type === 'credits'
			? 'Donut charts show credit transactions only.'
			: m.txn_chart_debits_only_hint()
	);
</script>

<div class="grid gap-4 lg:grid-cols-2">
	<Card>
		<CardHeader class="pb-2">
			<CardTitle>{accountTitle}</CardTitle>
			<p class="text-muted-foreground text-xs">{hintMessage}</p>
		</CardHeader>
		<CardContent>
			{#if hasAccountData}
				<Chart.Container config={accountConfig} class="min-h-70 w-full">
					<PieChart
						data={accountData}
						key="key"
						label="label"
						value="value"
						c="key"
						maxValue={accountMaxValue}
						innerRadius={0.65}
						padAngle={0}
						legend={false}
					>
						{#snippet tooltip()}
							<Chart.Tooltip />
						{/snippet}
					</PieChart>
				</Chart.Container>
			{:else}
				<div
					class="text-muted-foreground bg-muted/30 border-border/70 flex min-h-70 items-center justify-center rounded-md border border-dashed text-sm"
				>
					{emptyMessage}
				</div>
			{/if}
		</CardContent>
	</Card>

	<Card>
		<CardHeader class="pb-2">
			<CardTitle>{categoryTitle}</CardTitle>
			<p class="text-muted-foreground text-xs">{hintMessage}</p>
		</CardHeader>
		<CardContent>
			{#if hasCategoryData}
				<Chart.Container config={categoryConfig} class="min-h-70 w-full">
					<PieChart
						data={categoryData}
						key="key"
						label="label"
						value="value"
						c="key"
						maxValue={categoryMaxValue}
						innerRadius={0.65}
						padAngle={0}
						legend={false}
					>
						{#snippet tooltip()}
							<Chart.Tooltip />
						{/snippet}
					</PieChart>
				</Chart.Container>
			{:else}
				<div
					class="text-muted-foreground bg-muted/30 border-border/70 flex min-h-70 items-center justify-center rounded-md border border-dashed text-sm"
				>
					{emptyMessage}
				</div>
			{/if}
		</CardContent>
	</Card>
</div>
