<script lang="ts">
    import type {
        Account,
        AccountBalance,
        BalanceCreate,
        BalanceBatchCreate,
    } from '$lib/types';
    import { AccountType } from '$lib/types';
    import {
        Card,
        CardHeader,
        CardTitle,
        CardDescription,
        CardContent,
        CardFooter,
    } from '$lib/components/ui/card';
    import { Button } from '$lib/components/ui/button';
    import AccountBalanceChart from './account-balance-chart.svelte';
    import AddBalanceDialog from './add-balance-dialog.svelte';
    import { formatCurrency, formatDate } from '$lib/format';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        account: (Account & { institution_name?: string }) | Account;
        latestBalance: AccountBalance | null;
        balances: AccountBalance[];
        onCreateBalance: (data: BalanceCreate) => Promise<void>;
        onCreateBalanceBatch: (data: BalanceBatchCreate) => Promise<void>;
    }

    let {
        account,
        latestBalance,
        balances,
        onCreateBalance,
        onCreateBalanceBatch,
    }: Props = $props();

    const accountTypeLabelByValue: Record<string, string> = {
        [AccountType.BANKING]: m.account_type_banking(),
        [AccountType.TREASURY]: m.account_type_treasury(),
        [AccountType.CREDIT_CARD]: m.account_type_credit_card(),
        [AccountType.INVESTMENT]: m.account_type_investment(),
    };

    const institutionName = $derived(
        'institution_name' in account && account.institution_name
            ? account.institution_name
            : undefined
    );
    const accountTypeLabel = $derived(
        accountTypeLabelByValue[account.account_type] ?? account.account_type
    );

    const balanceText = $derived(
        latestBalance ? formatCurrency(latestBalance.balance / 100) : m.balance_no_data()
    );

    const updatedText = $derived(
        latestBalance
            ? m.balance_updated({ date: formatDate(new Date(latestBalance.balance_date)) })
            : ''
    );

    let addBalanceOpen = $state(false);
    let addBalanceLoading = $state(false);
    let addBalanceError = $state('');
    let addBalanceFieldErrors = $state<{
        balance?: string;
        balance_date?: string;
    }>({});

    function openAddBalance() {
        addBalanceError = '';
        addBalanceFieldErrors = {};
        addBalanceOpen = true;
    }

    function validateBalanceForm(data: BalanceCreate): boolean {
        addBalanceFieldErrors = {};
        let valid = true;
        if (!data.balance_date) {
            addBalanceFieldErrors.balance_date = m.balance_validation_date_required();
            valid = false;
        }
        if (!Number.isFinite(data.balance)) {
            addBalanceFieldErrors.balance = m.balance_validation_balance_required();
            valid = false;
        }
        return valid;
    }

    async function handleCreateBalance(data: BalanceCreate) {
        addBalanceError = '';
        if (!validateBalanceForm(data)) return;

        addBalanceLoading = true;
        try {
            await onCreateBalance(data);
            addBalanceOpen = false;
        } catch (e) {
            addBalanceError =
                e instanceof Error ? e.message : m.balance_error_add();
        } finally {
            addBalanceLoading = false;
        }
    }

    async function handleCreateBalanceBatch(data: BalanceBatchCreate) {
        addBalanceError = '';
        addBalanceLoading = true;
        try {
            await onCreateBalanceBatch(data);
            addBalanceOpen = false;
        } catch (e) {
            addBalanceError =
                e instanceof Error ? e.message : m.balance_error_add_batch();
        } finally {
            addBalanceLoading = false;
        }
    }
</script>

<Card class="h-full flex flex-col">
    <CardHeader class="pb-3">
        <CardTitle class="text-lg">{account.account_name}</CardTitle>
        <CardDescription class="flex flex-col gap-0.5">
            <span>{institutionName ?? m.balance_unknown_institution()}</span>
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
            <div class="text-sm text-muted-foreground mt-1">
                {m.balance_add_hint()}
            </div>
        {/if}

        <div class="mt-4">
            <AccountBalanceChart {balances} />
        </div>
    </CardContent>

    <CardFooter class="justify-end gap-2">
        <Button variant="outline" size="sm" disabled title={m.balance_coming_soon()}
            >{m.balance_edit()}</Button
        >
        <Button
            size="sm"
            onclick={openAddBalance}
            disabled={!account.tracks_balances}>{m.balance_add()}</Button
        >
    </CardFooter>
</Card>

<AddBalanceDialog
    open={addBalanceOpen}
    accountName={account.account_name}
    accountId={account.account_id}
    loading={addBalanceLoading}
    error={addBalanceError}
    fieldErrors={addBalanceFieldErrors}
    existingBalances={balances}
    onOpenChange={(open) => {
        addBalanceOpen = open;
    }}
    onSubmit={handleCreateBalance}
    onSubmitBatch={handleCreateBalanceBatch}
/>
