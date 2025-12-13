<script lang="ts">
  import type { Account, AccountBalance } from "$lib/types";
  import { AccountType } from "$lib/types";
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import BalanceChartPlaceholder from "./balance-chart-placeholder.svelte";
    import PlaceholderChart from "./placeholder-chart.svelte";

  interface Props {
    account: (Account & { institution_name?: string }) | Account;
    latestBalance: AccountBalance | null;
  }

  let { account, latestBalance }: Props = $props();

  const currency = new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" });
  const dateFmt = new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" });

  const accountTypeLabelByValue: Record<string, string> = {
    [AccountType.CHECKING]: "Checking",
    [AccountType.CREDIT_CARD]: "Credit Card",
    [AccountType.SAVINGS]: "Savings",
    [AccountType.INVESTMENT]: "Investment",
    [AccountType.RETIREMENT]: "Retirement",
    [AccountType.BROKERAGE]: "Brokerage",
  };

  const institutionName = $derived(("institution_name" in account && account.institution_name) ? account.institution_name : undefined);
  const accountTypeLabel = $derived(accountTypeLabelByValue[account.account_type] ?? account.account_type);

  const balanceText = $derived(
    latestBalance ? currency.format(latestBalance.balance / 100) : "No data"
  );

  const updatedText = $derived(
    latestBalance ? `Updated ${dateFmt.format(new Date(latestBalance.balance_date))}` : ""
  );
</script>

<Card class="h-full flex flex-col">
  <CardHeader class="pb-3">
    <CardTitle class="text-lg">{account.account_name}</CardTitle>
    <CardDescription class="flex flex-col gap-0.5">
      <span>{institutionName ?? "Unknown institution"}</span>
      <span>{accountTypeLabel}</span>
    </CardDescription>
  </CardHeader>

  <CardContent class="flex-1">
    <div class="text-3xl font-semibold tracking-tight">
      {balanceText}
    </div>
    {#if latestBalance}
      <div class="text-sm text-muted-foreground mt-1">{updatedText}</div>
    {:else}
      <div class="text-sm text-muted-foreground mt-1">Add a balance to see trends.</div>
    {/if}

    <div class="mt-4">
      <PlaceholderChart />
    </div>
  </CardContent>

  <CardFooter class="justify-end gap-2">
    <Button variant="outline" size="sm" disabled title="Coming soon">Edit</Button>
    <Button size="sm" disabled title="Coming soon">Add Balance</Button>
  </CardFooter>
</Card>

