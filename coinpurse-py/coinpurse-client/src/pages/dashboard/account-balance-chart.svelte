<script lang="ts">
    import type { AccountBalance } from '$lib/types';
    import { AreaChart } from 'layerchart';
    import { curveLinear } from 'd3-shape';
    import { scaleUtc } from 'd3-scale';
    import * as Chart from '$lib/components/ui/chart/index.js';

    interface Props {
        balances: AccountBalance[];
    }

    let { balances }: Props = $props();

    const compactCurrency = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        notation: 'compact',
        compactDisplay: 'short',
        maximumFractionDigits: 1,
    });

    function parseIsoDate(date: string): Date {
        // Ensure stable UTC date parsing for YYYY-MM-DD inputs
        return date.length === 10
            ? new Date(`${date}T00:00:00Z`)
            : new Date(date);
    }

    function sortKey(b: AccountBalance): string {
        return `${b.balance_date}|${b.created_at ?? ''}`;
    }

    const seriesBalances = $derived.by(() => {
        const byDate = new Map<string, AccountBalance>();
        for (const bal of balances ?? []) {
            const existing = byDate.get(bal.balance_date);
            if (!existing || sortKey(bal) > sortKey(existing))
                byDate.set(bal.balance_date, bal);
        }

        const sorted = [...byDate.values()].sort((a, b) =>
            sortKey(a).localeCompare(sortKey(b))
        );
        const MAX_POINTS = 90;
        return sorted.slice(-MAX_POINTS);
    });

    const chartData = $derived(
        seriesBalances.map((bal) => ({
            date: parseIsoDate(bal.balance_date),
            balance: bal.balance / 100,
        }))
    );

    const chartConfig = {
        balance: { label: 'Balance', color: 'var(--chart-1)' },
    } satisfies Chart.ChartConfig;

    const hasData = $derived(chartData.length >= 2);
</script>

{#if hasData}
    <Chart.Container config={chartConfig} class="min-h-[180px] w-full">
        <AreaChart
            data={chartData}
            x="date"
            xScale={scaleUtc()}
            series={[
                {
                    key: 'balance',
                    label: chartConfig.balance.label,
                    color: chartConfig.balance.color,
                },
            ]}
            props={{
                area: {
                    curve: curveLinear,
                    'fill-opacity': 0.35,
                    line: { class: 'stroke-2' },
                    motion: 'tween',
                },
                xAxis: {
                    format: (v: Date) =>
                        v.toLocaleDateString(undefined, {
                            day: '2-digit',
                            month: '2-digit',
                        }),
                },
                yAxis: {
                    format: (v) =>
                        typeof v === 'number'
                            ? compactCurrency.format(v)
                            : String(v),
                },
            }}
        >
            {#snippet tooltip()}
                <Chart.Tooltip
                    labelFormatter={(v: Date) =>
                        v.toLocaleDateString(undefined, {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                        })}
                    indicator="line"
                />
            {/snippet}
        </AreaChart>
    </Chart.Container>
{:else}
    <div
        class="min-h-[180px] w-full flex items-center justify-center text-sm text-muted-foreground bg-muted/30 border border-dashed rounded-md"
    >
        Add at least two balances to see a trend.
    </div>
{/if}
