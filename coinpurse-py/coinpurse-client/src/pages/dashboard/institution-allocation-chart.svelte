<script lang="ts">
	import { PieChart } from 'layerchart';
	import * as Chart from '$lib/components/ui/chart';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { type Account, type AccountBalance } from '$lib/types';
	import { formatCentsCurrency } from '$lib/format';

	interface Props {
		latestBalanceByAccountId: Record<number, AccountBalance>;
		balanceTrackingAccountById: Record<number, Account & { institution_name?: string }>;
	}

	let { latestBalanceByAccountId, balanceTrackingAccountById }: Props = $props();

	const chartData = $derived.by(() => {
		const totals = new Map<number, { name: string; total: number }>();
		for (const balance of Object.values(latestBalanceByAccountId)) {
			const account = balanceTrackingAccountById[balance.account_id];
			if (!account) continue;
			const id = account.institution_id;
			const existing = totals.get(id) ?? { name: account.institution_name ?? 'Unknown', total: 0 };
			totals.set(id, { ...existing, total: existing.total + balance.balance });
		}
		return [...totals.entries()]
			.filter(([, v]) => v.total > 0)
			.sort((a, b) => b[1].total - a[1].total)
			.map(([id, { name, total }], i) => ({
				key: `inst_${id}`,
				label: name,
				value: total,
				color: `var(--chart-${(i % 5) + 1})`,
			}));
	});

	const chartConfig = $derived(
		chartData.reduce(
			(config, item) => {
				config[item.key] = { label: item.label, color: item.color };
				return config;
			},
			{} as Chart.ChartConfig,
		),
	);

	const totalValue = $derived(chartData.reduce((sum, item) => sum + item.value, 0));
	const hasData = $derived(chartData.length > 0);
</script>

<Card>
	<CardHeader class="pb-2">
		<CardTitle>By Institution</CardTitle>
	</CardHeader>
	<CardContent>
		{#if hasData}
			<Chart.Container config={chartConfig} class="min-h-70 w-full">
				<PieChart
					data={chartData}
					key="key"
					label="label"
					value="value"
					c="key"
					maxValue={totalValue}
					innerRadius={0.65}
					padAngle={0}
					legend={false}
				>
					{#snippet tooltip()}
						<Chart.Tooltip hideLabel>
							{#snippet formatter({ value, name, item })}
								<div class="flex w-full items-center gap-2">
									<div
										style="--color-bg: {item.color}; --color-border: {item.color};"
										class="size-2.5 shrink-0 rounded-[2px] border-(--color-border) bg-(--color-bg)"
									></div>
									<span class="text-muted-foreground">{chartConfig[item.key]?.label ?? name}</span>
									<span class="text-foreground ml-auto font-mono font-medium tabular-nums">
										{formatCentsCurrency(value as number)}
									</span>
								</div>
							{/snippet}
						</Chart.Tooltip>
					{/snippet}
				</PieChart>
			</Chart.Container>
		{:else}
			<div
				class="text-muted-foreground bg-muted/30 border-border/70 flex min-h-70 items-center justify-center rounded-md border border-dashed text-sm"
			>
				No balance data available.
			</div>
		{/if}
	</CardContent>
</Card>
