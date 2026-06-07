<script lang="ts">
	import { PieChart } from 'layerchart';
	import * as Chart from '$lib/components/ui/chart';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { TaxTreatmentType, type Account, type AccountBalance } from '$lib/types';
	import { formatCentsCurrency } from '$lib/format';
	import * as m from '$lib/paraglide/messages';

	interface Props {
		latestBalanceByAccountId: Record<number, AccountBalance>;
		balanceTrackingAccountById: Record<number, Account & { institution_name?: string }>;
	}

	let { latestBalanceByAccountId, balanceTrackingAccountById }: Props = $props();

	const allSlices = [
		{ key: 'taxable', label: m.tax_taxable(), type: TaxTreatmentType.TAXABLE, color: 'var(--chart-1)' },
		{ key: 'tax_deferred', label: m.tax_deferred(), type: TaxTreatmentType.TAX_DEFERRED, color: 'var(--chart-2)' },
		{ key: 'tax_free', label: m.tax_free(), type: TaxTreatmentType.TAX_FREE, color: 'var(--chart-3)' },
		{ key: 'triple_tax_free', label: m.tax_triple_free(), type: TaxTreatmentType.TRIPLE_TAX_FREE, color: 'var(--chart-4)' },
		{ key: 'not_applicable', label: m.tax_not_applicable(), type: TaxTreatmentType.NOT_APPLICABLE, color: 'var(--chart-5)' },
	];

	const chartData = $derived(
		allSlices
			.map((slice) => {
				const total = Object.values(latestBalanceByAccountId).reduce((sum, balance) => {
					const account = balanceTrackingAccountById[balance.account_id];
					if (account?.tax_treatment === slice.type) return sum + balance.balance;
					return sum;
				}, 0);
				return { key: slice.key, label: slice.label, value: total, color: slice.color };
			})
			.filter((slice) => slice.value > 0),
	);

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
		<CardTitle>Tax Allocation</CardTitle>
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
