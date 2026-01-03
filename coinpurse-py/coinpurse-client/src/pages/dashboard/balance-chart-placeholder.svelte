<script lang="ts">
  import { Card, CardContent } from "$lib/components/ui/card";

  interface Props {
    accountId: number;
  }

  let { accountId }: Props = $props();
</script>

<Card class="bg-muted/30 border-dashed">
  <CardContent class="py-3">
    <div class="text-sm text-muted-foreground">
      Balance history chart - coming soon
    </div>

    <!--
      Future chart structure:
      - fetch balances for {accountId}
      - render line chart (e.g. Chart.js / ECharts)
      - time range controls (1M/3M/1Y/All)
      - hover tooltip, min/max markers
    -->
  </CardContent>
</Card>

