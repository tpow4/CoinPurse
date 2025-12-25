<script lang="ts">
  import type { AccountBalance, BalanceCreate } from "$lib/types";
  import * as Dialog from "$lib/components/ui/dialog";
  import * as Field from "$lib/components/ui/field";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";

  interface Props {
    open: boolean;
    accountName: string;
    loading?: boolean;
    error?: string;
    fieldErrors?: {
      balance?: string;
      balance_date?: string;
    };
    onOpenChange: (open: boolean) => void;
    onSubmit: (data: BalanceCreate) => Promise<AccountBalance | void> | AccountBalance | void;
    accountId: number;
    defaultBalanceDate?: string;
  }

  let {
    open = false,
    accountName,
    accountId,
    defaultBalanceDate,
    loading = false,
    error = "",
    fieldErrors = {},
    onOpenChange,
    onSubmit,
  }: Props = $props();

  type FormData = {
    balance: string;
    balance_date: string;
  };

  let localFieldErrors = $state<{ balance?: string }>({});

  function todayIsoDate(): string {
    return new Date().toISOString().slice(0, 10);
  }

  function initialBalanceDate(): string {
    return defaultBalanceDate ?? todayIsoDate();
  }

  function parseMoneyToCents(input: string): number | null {
    const trimmed = input.trim().replaceAll(",", "");
    if (!trimmed) return null;

    const match = trimmed.match(/^(-)?(\d+)(?:\.(\d{0,2}))?$/);
    if (!match) return null;

    const sign = match[1] ? -1 : 1;
    const dollarsPart = match[2] ?? "0";
    const centsPart = (match[3] ?? "").padEnd(2, "0");
    const dollars = Number(dollarsPart);
    const cents = Number(centsPart || "0");

    if (!Number.isFinite(dollars) || !Number.isFinite(cents)) return null;
    return sign * (dollars * 100 + cents);
  }

  let formData = $state<FormData>({ balance: "", balance_date: initialBalanceDate() });

  // Reset form when opened/closed or account changes
  $effect(() => {
    if (!open) return;
    formData.balance = "";
    formData.balance_date = initialBalanceDate();
    localFieldErrors = {};
  });

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    const cents = parseMoneyToCents(formData.balance);
    if (cents === null) {
      localFieldErrors = { balance: "Enter a valid number (e.g., 1234.56)" };
      return;
    }
    await onSubmit({
      account_id: accountId,
      balance_date: formData.balance_date,
      balance: cents,
    });
  }
</script>

<Dialog.Root {open} {onOpenChange}>
  <Dialog.Content class="sm:max-w-[480px]">
    <Dialog.Header>
      <Dialog.Title>Add Balance</Dialog.Title>
      <Dialog.Description>Record a balance for {accountName}.</Dialog.Description>
    </Dialog.Header>

    <form onsubmit={handleSubmit}>
      <div class="space-y-4">
        {#if error}
          <div class="bg-red-50 text-red-700 p-4 rounded">{error}</div>
        {/if}

        <Field.Field data-invalid={fieldErrors.balance || localFieldErrors.balance ? true : undefined}>
          <Field.Label for="balance">Balance</Field.Label>
          <Input
            id="balance"
            inputmode="decimal"
            placeholder="e.g., 1234.56"
            bind:value={formData.balance}
            aria-invalid={fieldErrors.balance || localFieldErrors.balance ? true : undefined}
            oninput={() => {
              localFieldErrors.balance = "";
            }}
          />
          {#if fieldErrors.balance || localFieldErrors.balance}
            <Field.Error>{fieldErrors.balance ?? localFieldErrors.balance}</Field.Error>
          {/if}
        </Field.Field>

        <Field.Field data-invalid={fieldErrors.balance_date ? true : undefined}>
          <Field.Label for="balance_date">Date</Field.Label>
          <Input
            id="balance_date"
            type="date"
            bind:value={formData.balance_date}
            aria-invalid={fieldErrors.balance_date ? true : undefined}
          />
          {#if fieldErrors.balance_date}
            <Field.Error>{fieldErrors.balance_date}</Field.Error>
          {/if}
        </Field.Field>

        <div class="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onclick={() => onOpenChange(false)} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </Button>
        </div>
      </div>
    </form>
  </Dialog.Content>
</Dialog.Root>
