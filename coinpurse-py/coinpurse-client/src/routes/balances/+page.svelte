<script lang="ts">
    import { ApiException } from "$lib/api";
    import type {
        Account,
        AccountBalance,
        AccountDueForCheckin,
        Institution,
        BalanceCreate,
        BalanceBatchCreate,
    } from "$lib/types";
    import { AccountType } from "$lib/types";

    import { Button } from "$lib/components/ui/button";
    import { Badge } from "$lib/components/ui/badge";
    import AccountBalanceCard from "../../pages/dashboard/account-balance-card.svelte";
    import StackedBalanceChart from "../../pages/dashboard/stacked-balance-chart.svelte";
    import BalanceCheckinDialog from "$lib/components/balance-checkin-dialog.svelte";
    import { accountsApi } from "$lib/api/accounts";
    import { institutionsApi } from "$lib/api/institutions";
    import { balancesApi } from "$lib/api/balances";
    import { settingsApi } from "$lib/api/settings";
    import { toast } from "svelte-sonner";
    import * as m from "$lib/paraglide/messages";

    type AccountWithInstitutionName = Account & { institution_name?: string };

    let accounts = $state<Account[]>([]);
    let institutions = $state<Institution[]>([]);
    let balances = $state<AccountBalance[]>([]);
    let dueAccounts = $state<AccountDueForCheckin[]>([]);

    let loading = $state(false);
    let error = $state("");
    let checkinDialogOpen = $state(false);
    let chartRefreshKey = $state(0);

    $effect(() => {
        loadData();
    });

    const institutionNameById = $derived(
        institutions.reduce(
            (map, inst) => {
                map[inst.institution_id] = inst.name;
                return map;
            },
            {} as Record<number, string>,
        ),
    );

    const latestBalanceByAccountId = $derived(
        getLatestBalanceByAccountId(balances),
    );
    const balancesByAccountId = $derived(
        balances.reduce(
            (map, bal) => {
                (map[bal.account_id] ??= []).push(bal);
                return map;
            },
            {} as Record<number, AccountBalance[]>,
        ),
    );
    const previousBalanceByAccountId = $derived(
        getPreviousBalanceByAccountId(balancesByAccountId),
    );

    const accountsWithInstitutionName = $derived(
        accounts
            .map(
                (account) =>
                    ({
                        ...account,
                        institution_name:
                            institutionNameById[account.institution_id] ??
                            "Unknown",
                    }) satisfies AccountWithInstitutionName,
            )
            .sort(
                (a, b) =>
                    (a.display_order ?? 0) - (b.display_order ?? 0) ||
                    a.account_name.localeCompare(b.account_name),
            ),
    );

    const balanceTrackingAccountsWithInstitutionName = $derived(
        accountsWithInstitutionName.filter((a) => a.tracks_balances),
    );

    const allCheckinAccounts = $derived<AccountDueForCheckin[]>(
        balanceTrackingAccountsWithInstitutionName.map((a) => ({
            account_id: a.account_id,
            account_name: a.account_name,
            institution_name: a.institution_name ?? "Unknown",
            last_balance_date:
                latestBalanceByAccountId[a.account_id]?.balance_date ?? null,
            days_since_last: null,
        })),
    );

    const balanceTrackingAccountById = $derived(
        balanceTrackingAccountsWithInstitutionName.reduce(
            (map, account) => {
                map[account.account_id] = account;
                return map;
            },
            {} as Record<number, AccountWithInstitutionName>,
        ),
    );

    const netWorthTotal = $derived(
        Object.values(latestBalanceByAccountId).reduce((sum, balance) => {
            if (!balanceTrackingAccountById[balance.account_id]) return sum;
            return sum + balance.balance;
        }, 0),
    );

    const liquidTotal = $derived(
        Object.values(latestBalanceByAccountId).reduce((sum, balance) => {
            const account = balanceTrackingAccountById[balance.account_id];
            if (!account) return sum;
            if (
                account.account_type === AccountType.BANKING ||
                account.account_type === AccountType.TREASURY
            ) {
                return sum + balance.balance;
            }
            return sum;
        }, 0),
    );

    const netWorthPreviousTotal = $derived(
        Object.values(latestBalanceByAccountId).reduce((sum, latest) => {
            if (!balanceTrackingAccountById[latest.account_id]) return sum;
            const previous = previousBalanceByAccountId[latest.account_id];
            return sum + (previous ? previous.balance : latest.balance);
        }, 0),
    );

    const netWorthChange = $derived(netWorthTotal - netWorthPreviousTotal);
    const netWorthChangePercent = $derived(
        netWorthPreviousTotal !== 0
            ? netWorthChange / netWorthPreviousTotal
            : 0,
    );
    const hasPreviousBalances = $derived(
        Object.keys(previousBalanceByAccountId).some(
            (accountId) => balanceTrackingAccountById[Number(accountId)],
        ),
    );

    const latestBalanceOverall = $derived(
        Object.values(latestBalanceByAccountId).reduce(
            (latest, balance) => {
                if (!balanceTrackingAccountById[balance.account_id]) {
                    return latest;
                }
                if (!latest) return balance;
                return balanceKey(balance) > balanceKey(latest)
                    ? balance
                    : latest;
            },
            null as AccountBalance | null,
        ),
    );

    async function loadData() {
        loading = true;
        error = "";
        try {
            const [
                accountsData,
                institutionsData,
                balancesData,
                dueAccountsData,
            ] = await Promise.all([
                accountsApi.getAll(false),
                institutionsApi.getAll(false),
                balancesApi.getAll(),
                settingsApi.getAccountsDueForCheckin().catch(() => []),
            ]);
            accounts = accountsData;
            institutions = institutionsData;
            balances = balancesData;
            dueAccounts = dueAccountsData;
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = m.balances_error_load();
            }
        } finally {
            loading = false;
        }
    }

    function getLatestBalanceByAccountId(allBalances: AccountBalance[]) {
        return allBalances.reduce(
            (map, bal) => {
                const existing = map[bal.account_id];
                if (!existing) {
                    map[bal.account_id] = bal;
                    return map;
                }
                const existingKey = `${existing.balance_date}|${existing.created_at}`;
                const balKey = `${bal.balance_date}|${bal.created_at}`;
                if (balKey > existingKey) map[bal.account_id] = bal;
                return map;
            },
            {} as Record<number, AccountBalance>,
        );
    }

    function getPreviousBalanceByAccountId(
        groupedBalances: Record<number, AccountBalance[]>,
    ) {
        const previousById: Record<number, AccountBalance> = {};
        Object.entries(groupedBalances).forEach(([accountId, list]) => {
            if (list.length < 2) return;
            const sorted = list
                .slice()
                .sort((a, b) => balanceKey(a).localeCompare(balanceKey(b)));
            previousById[Number(accountId)] = sorted[sorted.length - 2];
        });
        return previousById;
    }

    function balanceKey(balance: AccountBalance) {
        return `${balance.balance_date}|${balance.created_at}`;
    }

    async function handleCreateBalance(data: BalanceCreate) {
        const created = await balancesApi.create(data);
        balances = [...balances, created];
        chartRefreshKey += 1;
    }

    async function handleCreateBalanceBatch(data: BalanceBatchCreate) {
        const result = await balancesApi.createBatch(data);
        const updatedIds = new Set(result.balances.map((b) => b.balance_id));
        balances = [
            ...balances.filter((b) => !updatedIds.has(b.balance_id)),
            ...result.balances,
        ];
        chartRefreshKey += 1;
    }
</script>

<div class="mx-auto max-w-350 p-8">
    <div class="mb-8 flex items-start justify-between gap-4">
        <div>
            <h1 class="mb-2 text-3xl font-bold">{m.balances_title()}</h1>
            <p class="text-muted-foreground">
                {m.balances_description()}
            </p>
        </div>
        <div class="flex gap-2">
            <Button
                onclick={() => {
                    checkinDialogOpen = true;
                }}
            >
                {m.checkin_btn()}
                {#if dueAccounts.length > 0}
                    <Badge variant="destructive">{dueAccounts.length}</Badge>
                {/if}
            </Button>
        </div>
    </div>

    {#if error}
        <div class="mb-6 rounded bg-red-50 p-4 text-red-700">{error}</div>
    {/if}

    {#if !loading && balanceTrackingAccountsWithInstitutionName.length > 0}
        <div class="mb-8">
            {#key chartRefreshKey}
                <StackedBalanceChart
                    {netWorthTotal}
                    {netWorthChange}
                    {netWorthChangePercent}
                    {liquidTotal}
                    {hasPreviousBalances}
                    lastUpdatedDate={latestBalanceOverall?.balance_date ?? null}
                />
            {/key}
        </div>
    {/if}

    {#if loading}
        <div class="py-12 text-center text-gray-600">
            {m.balances_loading()}
        </div>
    {:else if balanceTrackingAccountsWithInstitutionName.length === 0}
        <div class="text-muted-foreground py-12 text-center">
            {m.balances_empty()}
        </div>
    {:else}
        <div
            class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
        >
            {#each balanceTrackingAccountsWithInstitutionName as account (account.account_id)}
                <AccountBalanceCard
                    {account}
                    latestBalance={latestBalanceByAccountId[
                        account.account_id
                    ] ?? null}
                    balances={balancesByAccountId[account.account_id] ?? []}
                    onCreateBalance={handleCreateBalance}
                    onCreateBalanceBatch={handleCreateBalanceBatch}
                />
            {/each}
        </div>
    {/if}
</div>

<BalanceCheckinDialog
    open={checkinDialogOpen}
    accounts={dueAccounts.length > 0 ? dueAccounts : allCheckinAccounts}
    onOpenChange={(open) => {
        checkinDialogOpen = open;
    }}
    onSuccess={() => {
        loadData();
        sessionStorage.removeItem("balance_checkin_reminded");
        toast.success(m.checkin_success());
    }}
/>
