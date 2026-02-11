<script lang="ts">
	import type { TransactionWithNames } from '$lib/types';
	import { LineChart } from 'layerchart';
	import * as Chart from '$lib/components/ui/chart';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { formatDateCompact } from '$lib/format';

	interface Props {
		transactions: TransactionWithNames[];
	}

	interface MonthlyRatioDatum {
		monthLabel: string;
		ratio: number;
	}

	let { transactions }: Props = $props();

	function parseIsoDate(date: string): Date {
		// Ensure stable UTC date parsing for YYYY-MM-DD inputs.
		return date.length === 10 ? new Date(`${date}T00:00:00Z`) : new Date(date);
	}

	const chartData = $derived.by(() => {
		const byMonth = new Map<
			string,
			{ monthDate: Date; creditCents: number; debitCentsAbs: number }
		>();

		for (const tx of transactions) {
			const date = parseIsoDate(tx.transaction_date);
			if (Number.isNaN(date.getTime())) continue;

			const monthDate = new Date(
				Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1)
			);
			const monthKey = monthDate.toISOString().slice(0, 7);
			const current = byMonth.get(monthKey) ?? {
				monthDate,
				creditCents: 0,
				debitCentsAbs: 0,
			};

			if (tx.amount > 0) current.creditCents += tx.amount;
			if (tx.amount < 0) current.debitCentsAbs += Math.abs(tx.amount);

			byMonth.set(monthKey, current);
		}

		return [...byMonth.entries()]
			.sort((a, b) => a[0].localeCompare(b[0]))
			.map(([, value]): MonthlyRatioDatum => ({
				monthLabel: formatDateCompact(value.monthDate),
				ratio:
					value.debitCentsAbs > 0 ? value.creditCents / value.debitCentsAbs : 0,
			}));
	});

	const chartConfig = {
		ratio: { label: 'Credit / Debit Ratio', color: 'var(--chart-2)' },
	} satisfies Chart.ChartConfig;

	const hasData = $derived(chartData.length > 0);
</script>

<Card>
	<CardHeader class="pb-2">
		<CardTitle>Credit/Debit Ratio by Month</CardTitle>
		<p class="text-muted-foreground text-xs">
			Values above 1.0x indicate credits exceeded debits.
		</p>
	</CardHeader>
	<CardContent>
		{#if hasData}
			<Chart.Container config={chartConfig} class="min-h-70 w-full">
				<LineChart
					data={chartData}
					x="monthLabel"
					series={[
						{
							key: 'ratio',
							label: chartConfig.ratio.label,
							value: (d: MonthlyRatioDatum) => d.ratio,
							color: chartConfig.ratio.color,
						},
					]}
					props={{
						yAxis: {
							format: (v) =>
								typeof v === 'number' ? `${v.toFixed(2)}x` : String(v),
						},
					}}
				>
					{#snippet tooltip()}
						<Chart.Tooltip labelKey="monthLabel" indicator="line">
							{#snippet formatter({ value, name })}
								<div class="flex w-full items-center justify-between gap-2">
									<span class="text-muted-foreground">{name}</span>
									<span class="font-mono font-medium tabular-nums">
										{Number(value).toFixed(2)}x
									</span>
								</div>
							{/snippet}
						</Chart.Tooltip>
					{/snippet}
				</LineChart>
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
