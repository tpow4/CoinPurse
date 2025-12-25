<script lang="ts">
  import { onMount } from 'svelte';
  import { AreaChart } from 'layerchart';
  import { curveMonotoneX } from 'd3-shape';
  import { scaleUtc } from 'd3-scale';
  import * as Chart from '$lib/components/ui/chart/index.js';
  import { balancesApi } from '$lib/api/balances';
  import { ApiException } from '$lib/api';
  import type { MonthlyBalanceAggregateResponse } from '$lib/types';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';

  let loading = $state(true);
  let error = $state('');
  let response = $state<MonthlyBalanceAggregateResponse | null>(null);

  const compactCurrency = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1,
  });

  const currency = new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  });

  function parseIsoDate(date: string): Date {
    // Ensure stable UTC date parsing for YYYY-MM-DD inputs
    return date.length === 10 ? new Date(`${date}T00:00:00Z`) : new Date(date);
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
        const monthData = accountSeries.data.find((d) => d.balance_date === monthDate);
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

  onMount(async () => {
    loading = true;
    error = '';

    try {
      const data = await balancesApi.getAggregatedMonthly();
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
  });
</script>

{#if error}
  <div class="bg-red-50 text-red-700 p-4 rounded">
    Failed to load portfolio chart: {error}
  </div>
{:else if loading}
  <div class="h-[400px] flex items-center justify-center text-sm text-muted-foreground">
    Loading portfolio chart...
  </div>
{:else if !hasData}
  <div
    class="h-[400px] flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-md"
  >
    Add balance data to your accounts to see portfolio trends.
  </div>
{:else}
  <Card class="h-full flex flex-col">
    <CardHeader class="pb-3">
        <CardTitle class="text-lg">{"Portfolio Overview"}</CardTitle>
    </CardHeader>
    <CardContent class="flex-1">
    <Chart.Container config={chartConfig} class="h-[400px] w-full">
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
                v.toLocaleDateString(undefined, { month: 'short', year: 'numeric' }),
            },
            yAxis: {
            format: (v) => (typeof v === 'number' ? compactCurrency.format(v) : String(v)),
            },
        }}
        >
        {#snippet tooltip()}
            <Chart.Tooltip
            labelFormatter={(v: Date) =>
                v.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })}
            indicator="line"
            />
        {/snippet}
        </AreaChart>
    </Chart.Container>
  </CardContent>
</Card>
{/if}
