<script lang="ts">
  import type { Account, AccountBalance, BalanceCreate } from "$lib/types";
  import { AccountType } from "$lib/types";
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import AccountBalanceChart from "./account-balance-chart.svelte";
  import AddBalanceDialog from "./add-balance-dialog.svelte";

  interface Props {
    account: (Account & { institution_name?: string }) | Account;
    latestBalance: AccountBalance | null;
    balances: AccountBalance[];
    onCreateBalance: (data: BalanceCreate) => Promise<void>;
  }

  let { account, latestBalance, balances, onCreateBalance }: Props = $props();

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

  let addBalanceOpen = $state(false);
  let addBalanceLoading = $state(false);
  let addBalanceError = $state("");
  let addBalanceFieldErrors = $state<{ balance?: string; balance_date?: string }>({});

  function openAddBalance() {
    addBalanceError = "";
    addBalanceFieldErrors = {};
    addBalanceOpen = true;
  }

  function validateBalanceForm(data: BalanceCreate): boolean {
    addBalanceFieldErrors = {};
    let valid = true;
    if (!data.balance_date) {
      addBalanceFieldErrors.balance_date = "Date is required";
      valid = false;
    }
    if (!Number.isFinite(data.balance)) {
      addBalanceFieldErrors.balance = "Balance is required";
      valid = false;
    }
    return valid;
  }

  async function handleCreateBalance(data: BalanceCreate) {
    addBalanceError = "";
    if (!validateBalanceForm(data)) return;

    addBalanceLoading = true;
    try {
      await onCreateBalance(data);
      addBalanceOpen = false;
    } catch (e) {
      addBalanceError = e instanceof Error ? e.message : "Failed to add balance";
    } finally {
      addBalanceLoading = false;
    }
  }
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
      <AccountBalanceChart balances={balances} />
    </div>
  </CardContent>

  <CardFooter class="justify-end gap-2">
    <Button variant="outline" size="sm" disabled title="Coming soon">Edit</Button>
    <Button size="sm" onclick={openAddBalance} disabled={!account.tracks_balances}>Add Balance</Button>
  </CardFooter>
</Card>

<AddBalanceDialog
  open={addBalanceOpen}
  accountName={account.account_name}
  accountId={account.account_id}
  loading={addBalanceLoading}
  error={addBalanceError}
  fieldErrors={addBalanceFieldErrors}
  onOpenChange={(open) => {
    addBalanceOpen = open;
  }}
  onSubmit={handleCreateBalance}
/>
