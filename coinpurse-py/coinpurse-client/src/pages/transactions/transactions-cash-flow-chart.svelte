<script lang="ts">
	import type { TransactionWithNames } from '$lib/types';
	import { BarChart } from 'layerchart';
	import * as Chart from '$lib/components/ui/chart';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { formatCompactCurrency, formatDateCompact } from '$lib/format';

	interface Props {
		transactions: TransactionWithNames[];
	}

	let { transactions }: Props = $props();

	interface MonthlyCashFlowDatum {
		monthLabel: string;
		cashFlow: number;
	}

	function parseIsoDate(date: string): Date {
		// Ensure stable UTC date parsing for YYYY-MM-DD inputs.
		return date.length === 10 ? new Date(`${date}T00:00:00Z`) : new Date(date);
	}

	const chartData = $derived.by(() => {
		const byMonth = new Map<string, { monthDate: Date; totalCents: number }>();

		for (const tx of transactions) {
			const date = parseIsoDate(tx.transaction_date);
			if (Number.isNaN(date.getTime())) continue;

			const monthDate = new Date(
				Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1)
			);
			const monthKey = monthDate.toISOString().slice(0, 7);
			const current = byMonth.get(monthKey);

			if (current) {
				current.totalCents += tx.amount;
			} else {
				byMonth.set(monthKey, { monthDate, totalCents: tx.amount });
			}
		}

		return [...byMonth.entries()]
			.sort((a, b) => a[0].localeCompare(b[0]))
			.map(([, value]): MonthlyCashFlowDatum => ({
				monthLabel: formatDateCompact(value.monthDate),
				cashFlow: value.totalCents / 100,
			}));
	});

	const chartConfig = {
		positiveCashFlow: { label: 'Positive Cash Flow', color: '#16a34a' },
		negativeCashFlow: { label: 'Negative Cash Flow', color: '#dc2626' },
	} satisfies Chart.ChartConfig;

	const hasData = $derived(chartData.length > 0);
</script>

<Card>
	<CardHeader class="pb-2">
		<CardTitle>Cash Flow by Month</CardTitle>
		<p class="text-muted-foreground text-xs">
			Shown when both credits and debits are included.
		</p>
	</CardHeader>
	<CardContent>
		{#if hasData}
			<Chart.Container config={chartConfig} class="min-h-70 w-full">
				<BarChart
					data={chartData}
					x="monthLabel"
					series={[
						{
							key: 'positiveCashFlow',
							label: chartConfig.positiveCashFlow.label,
							value: (d: MonthlyCashFlowDatum) =>
								d.cashFlow > 0 ? d.cashFlow : undefined,
							color: chartConfig.positiveCashFlow.color,
						},
						{
							key: 'negativeCashFlow',
							label: chartConfig.negativeCashFlow.label,
							value: (d: MonthlyCashFlowDatum) =>
								d.cashFlow < 0 ? d.cashFlow : undefined,
							color: chartConfig.negativeCashFlow.color,
						},
					]}
					props={{
						yAxis: {
							format: (v) =>
								typeof v === 'number' ? formatCompactCurrency(v) : String(v),
						},
					}}
				>
					{#snippet tooltip()}
						<Chart.Tooltip labelKey="monthLabel" indicator="line" />
					{/snippet}
				</BarChart>
			</Chart.Container>
		{:else}
			<div
				class="text-muted-foreground bg-muted/30 border-border/70 flex min-h-70 items-center justify-center rounded-md border border-dashed text-sm"
			>
				No transactions in the current filtered results.
			</div>
		{/if}
	</CardContent>
</Card>
