<script lang="ts">
    import { onMount } from 'svelte';
    import { AreaChart } from 'layerchart';
    import { curveMonotoneX } from 'd3-shape';
    import { scaleUtc } from 'd3-scale';
    import * as Chart from '$lib/components/ui/chart/index.js';
    import { balancesApi } from '$lib/api/balances';
    import { ApiException } from '$lib/api';
    import type { MonthlyBalanceAggregateResponse } from '$lib/types';
    import {
        Card,
        CardContent,
        CardHeader,
        CardTitle,
    } from '$lib/components/ui/card';
    import { ButtonGroup } from '$lib/components/ui/button-group';
    import { Button } from '$lib/components/ui/button';
    import { formatCompactCurrency, formatPercent, formatDate, formatDateCompact } from '$lib/format';

    type DateRange = 'ytd' | '1y' | 'max';

    interface Props {
        netWorthTotal: number;
        netWorthChange: number;
        netWorthChangePercent: number;
        liquidTotal: number;
        hasPreviousBalances: boolean;
        lastUpdatedDate: string | null;
    }

    let {
        netWorthTotal,
        netWorthChange,
        netWorthChangePercent,
        liquidTotal,
        hasPreviousBalances,
        lastUpdatedDate,
    }: Props = $props();

    let loading = $state(true);
    let error = $state('');
    let response = $state<MonthlyBalanceAggregateResponse | null>(null);
    let selectedRange = $state<DateRange>('ytd');

    const changeIsPositive = $derived(netWorthChange >= 0);
    const changeClass = $derived(
        changeIsPositive ? 'text-emerald-600' : 'text-red-600'
    );

    function parseIsoDate(date: string): Date {
        // Ensure stable UTC date parsing for YYYY-MM-DD inputs
        return date.length === 10
            ? new Date(`${date}T00:00:00Z`)
            : new Date(date);
    }

    // Transform API response to LayerChart format
    // API gives: { month_end_dates: [...], series: [{ account_id, data: [...] }] }
    // LayerChart needs: [{ date: Date, account_1: number, account_2: number, ... }]
    const chartData = $derived.by(() => {
        if (!response || !response.month_end_dates.length) return [];

        return response.month_end_dates.map((monthDate) => {
            const point: Record<string, Date | number> = {
                date: parseIsoDate(monthDate),
            };

            // Add each account's balance for this month
            response?.series.forEach((accountSeries) => {
                const monthData = accountSeries.data.find(
                    (d) => d.balance_date === monthDate
                );
                const key = `account_${accountSeries.account_id}`;
                // Convert cents to dollars
                point[key] = monthData ? monthData.balance / 100 : 0;
            });

            return point;
        });
    });

    // Build dynamic series configuration for LayerChart
    const chartSeries = $derived(
        response?.series.map((s, idx) => ({
            key: `account_${s.account_id}`,
            label: s.account_name,
            color: `var(--chart-${(idx % 5) + 1})`, // Cycle through chart-1 to chart-5
        })) ?? []
    );

    // Create chart config for tooltip/legend
    const chartConfig = $derived(
        chartSeries.reduce(
            (config, series) => {
                config[series.key] = {
                    label: series.label,
                    color: series.color,
                };
                return config;
            },
            {} as Record<string, { label: string; color: string }>
        )
    );

    const hasData = $derived(chartData.length >= 1 && chartSeries.length > 0);

    function getStartDateForRange(range: DateRange): string | undefined {
        if (range === 'max') return undefined;

        const now = new Date();
        let startDate: Date;

        if (range === 'ytd') {
            // Start of current year
            startDate = new Date(now.getFullYear(), 0, 1);
        } else {
            // 1 year ago
            startDate = new Date(
                now.getFullYear() - 1,
                now.getMonth(),
                now.getDate()
            );
        }

        return startDate.toISOString().split('T')[0];
    }

    async function fetchData() {
        loading = true;
        error = '';

        try {
            const startDate = getStartDateForRange(selectedRange);
            const data = await balancesApi.getAggregatedMonthly({
                start_date: startDate,
            });
            response = data;
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to load portfolio chart';
            }
        } finally {
            loading = false;
        }
    }

    function handleRangeChange(range: DateRange) {
        selectedRange = range;
        fetchData();
    }

    onMount(() => {
        fetchData();
    });
</script>

{#if error}
    <div class="bg-red-50 text-red-700 p-4 rounded">
        Failed to load portfolio chart: {error}
    </div>
{:else}
    <Card class="h-full flex flex-col">
        <CardHeader class="pb-2">
            <div
                class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between"
            >
                <div class="flex flex-col gap-1">
                    <CardTitle
                        class="text-xs uppercase tracking-wide text-muted-foreground"
                    >
                        Net worth
                    </CardTitle>
                    <div class="flex flex-row items-center gap-3">
                        <div class="text-3xl font-semibold tracking-tight">
                            {formatCompactCurrency(netWorthTotal / 100)}
                        </div>
                        <div class="flex flex-col pl-8 items-center text-xs">
                            <span
                                class="text-muted-foreground uppercase tracking-wide"
                            >
                                {#if lastUpdatedDate}
                                    {formatDate(
                                        parseIsoDate(lastUpdatedDate)
                                    )}
                                {:else}
                                    No balances yet
                                {/if}
                            </span>
                            {#if hasPreviousBalances}
                                <span class={changeClass}>
                                    {changeIsPositive ? '▲' : '▼'}
                                    {formatCompactCurrency(
                                        Math.abs(netWorthChange) / 100
                                    )}
                                    ({formatPercent(
                                        Math.abs(netWorthChangePercent)
                                    )})
                                </span>
                            {/if}
                        </div>
                    </div>
                </div>
                <div class="flex gap-6">
                    <div class="text-right">
                        <div
                            class="text-xs uppercase tracking-wide text-muted-foreground"
                        >
                            Liquid total
                        </div>
                        <div class="text-lg font-semibold">
                            {formatCompactCurrency(liquidTotal / 100)}
                        </div>
                    </div>
                </div>
            </div>
        </CardHeader>
        <CardContent class="flex-1">
            {#if loading}
                <div
                    class="h-[360px] flex items-center justify-center text-sm text-muted-foreground"
                >
                    Loading portfolio chart...
                </div>
            {:else if !hasData}
                <div
                    class="h-[360px] flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-md"
                >
                    Add balance data to your accounts to see portfolio trends.
                </div>
            {:else}
                <Chart.Container config={chartConfig} class="h-[360px] w-full">
                    <AreaChart
                        data={chartData}
                        x="date"
                        xScale={scaleUtc()}
                        series={chartSeries}
                        seriesLayout="stack"
                        props={{
                            area: {
                                curve: curveMonotoneX,
                                'fill-opacity': 0.4,
                                line: { class: 'stroke-1' },
                                motion: 'tween',
                            },
                            xAxis: {
                                format: (v: Date) =>
                                    formatDateCompact(v),
                            },
                            yAxis: {
                                format: (v) =>
                                    typeof v === 'number'
                                        ? formatCompactCurrency(v)
                                        : String(v),
                            },
                        }}
                    >
                        {#snippet tooltip()}
                            <Chart.Tooltip
                                labelFormatter={(v: Date) =>
                                    formatDateCompact(v)}
                                indicator="line"
                            />
                        {/snippet}
                    </AreaChart>
                </Chart.Container>
            {/if}
            <div class="mt-4 flex justify-center">
                <ButtonGroup>
                    <Button
                        variant={selectedRange === 'ytd'
                            ? 'default'
                            : 'outline'}
                        size="sm"
                        onclick={() => handleRangeChange('ytd')}
                    >
                        YTD
                    </Button>
                    <Button
                        variant={selectedRange === '1y' ? 'default' : 'outline'}
                        size="sm"
                        onclick={() => handleRangeChange('1y')}
                    >
                        1Y
                    </Button>
                    <Button
                        variant={selectedRange === 'max'
                            ? 'default'
                            : 'outline'}
                        size="sm"
                        onclick={() => handleRangeChange('max')}
                    >
                        Max
                    </Button>
                </ButtonGroup>
            </div>
        </CardContent>
    </Card>
{/if}
