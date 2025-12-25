<script lang="ts">
    import { ApiException } from '$lib/api';
    import type {
        Account,
        AccountBalance,
        AccountCreate,
        Institution,
        AccountType,
        BalanceCreate,
    } from '$lib/types';

    import { Button } from '$lib/components/ui/button';
    import AddEditAccountDialog from './accounts/add-edit-account-dialog.svelte';
    import AddEditInstitutionDialog from './institutions/add-edit-institution-dialog.svelte';
    import AccountBalanceCard from './dashboard/account-balance-card.svelte';
    import StackedBalanceChart from './dashboard/stacked-balance-chart.svelte';
    import { accountsApi } from '$lib/api/accounts';
    import { institutionsApi } from '$lib/api/institutions';
    import { balancesApi } from '$lib/api/balances';

    type AccountWithInstitutionName = Account & { institution_name?: string };

    let accounts = $state<Account[]>([]);
    let institutions = $state<Institution[]>([]);
    let balances = $state<AccountBalance[]>([]);

    let loading = $state(false);
    let error = $state('');

    let showAddAccount = $state(false);
    let showAddInstitution = $state(false);

    let accountFormLoading = $state(false);
    let accountFormError = $state('');
    let accountFieldErrors = $state({
        account_name: '',
        institution_id: '',
        account_type: '',
        last_4_digits: '',
    });

    let institutionFormLoading = $state(false);
    let institutionFormError = $state('');
    let institutionFieldErrors = $state({ name: '' });

    let institutionsRefreshKey = $state(0);
    let chartRefreshKey = $state(0);

    $effect(() => {
        loadDashboardData();
    });

    const institutionNameById = $derived(
        institutions.reduce(
            (map, inst) => {
                map[inst.institution_id] = inst.name;
                return map;
            },
            {} as Record<number, string>
        )
    );

    const latestBalanceByAccountId = $derived(
        getLatestBalanceByAccountId(balances)
    );
    const balancesByAccountId = $derived(
        balances.reduce(
            (map, bal) => {
                (map[bal.account_id] ??= []).push(bal);
                return map;
            },
            {} as Record<number, AccountBalance[]>
        )
    );

    const accountsWithInstitutionName = $derived(
        accounts
            .map(
                (account) =>
                    ({
                        ...account,
                        institution_name:
                            institutionNameById[account.institution_id] ??
                            'Unknown',
                    }) satisfies AccountWithInstitutionName
            )
            .sort(
                (a, b) =>
                    (a.display_order ?? 0) - (b.display_order ?? 0) ||
                    a.account_name.localeCompare(b.account_name)
            )
    );

    async function loadDashboardData() {
        loading = true;
        error = '';
        try {
            const [accountsData, institutionsData, balancesData] =
                await Promise.all([
                    accountsApi.getAll(false),
                    institutionsApi.getAll(false),
                    balancesApi.getAll(),
                ]);
            accounts = accountsData;
            institutions = institutionsData;
            balances = balancesData;
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to load dashboard';
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
            {} as Record<number, AccountBalance>
        );
    }

    function openAddAccount() {
        accountFormError = '';
        accountFieldErrors = {
            account_name: '',
            institution_id: '',
            account_type: '',
            last_4_digits: '',
        };
        showAddAccount = true;
    }

    function openAddInstitution() {
        institutionFormError = '';
        institutionFieldErrors = { name: '' };
        showAddInstitution = true;
    }

    function validateAccountForm(data: {
        account_name: string;
        institution_id: number;
        account_type: AccountType;
        last_4_digits: string;
    }): boolean {
        accountFieldErrors = {
            account_name: '',
            institution_id: '',
            account_type: '',
            last_4_digits: '',
        };
        let isValid = true;

        if (!data.account_name.trim()) {
            accountFieldErrors.account_name = 'Account name is required';
            isValid = false;
        } else if (data.account_name.length > 100) {
            accountFieldErrors.account_name =
                'Name is too long (max 100 characters)';
            isValid = false;
        }

        if (!data.institution_id || data.institution_id === 0) {
            accountFieldErrors.institution_id = 'Institution is required';
            isValid = false;
        }

        if (!data.account_type) {
            accountFieldErrors.account_type = 'Account type is required';
            isValid = false;
        }

        if (data.last_4_digits && data.last_4_digits.length > 4) {
            accountFieldErrors.last_4_digits =
                'Last 4 digits must be 4 characters or less';
            isValid = false;
        }

        return isValid;
    }

    async function handleCreateAccount(data: {
        account_name: string;
        institution_id: number;
        account_type: AccountType;
        account_subtype: string | null;
        last_4_digits: string;
        tracks_transactions: boolean;
        tracks_balances: boolean;
        display_order: number;
    }) {
        accountFormError = '';
        if (!validateAccountForm(data)) return;

        accountFormLoading = true;
        try {
            const createData: AccountCreate = {
                account_name: data.account_name,
                institution_id: data.institution_id,
                account_type: data.account_type,
                account_subtype: data.account_subtype,
                last_4_digits: data.last_4_digits,
                tracks_transactions: data.tracks_transactions,
                tracks_balances: data.tracks_balances,
                display_order: data.display_order,
                active: true,
            };
            await accountsApi.create(createData);
            showAddAccount = false;
            loadDashboardData();
        } catch (e) {
            if (e instanceof ApiException) {
                accountFormError = e.detail;
            } else {
                accountFormError = 'Failed to create account';
            }
        } finally {
            accountFormLoading = false;
        }
    }

    function validateInstitutionForm(name: string): boolean {
        institutionFieldErrors = { name: '' };
        if (!name.trim()) {
            institutionFieldErrors.name = 'Institution name is required';
            return false;
        }
        if (name.length > 100) {
            institutionFieldErrors.name =
                'Name is too long (max 100 characters)';
            return false;
        }
        return true;
    }

    async function handleCreateInstitution(data: { name: string }) {
        institutionFormError = '';
        if (!validateInstitutionForm(data.name)) return;

        institutionFormLoading = true;
        try {
            await institutionsApi.create({ name: data.name });
            showAddInstitution = false;
            institutionsRefreshKey += 1;
            loadDashboardData();
        } catch (e) {
            if (e instanceof ApiException) {
                institutionFormError = e.detail;
            } else {
                institutionFormError = 'Failed to create institution';
            }
        } finally {
            institutionFormLoading = false;
        }
    }

    async function handleCreateBalance(data: BalanceCreate) {
        const created = await balancesApi.create(data);
        balances = [...balances, created];
        chartRefreshKey += 1; // Trigger chart refresh
    }
</script>

<div class="p-8 max-w-[1400px] mx-auto">
    <div class="flex items-start justify-between gap-4 mb-8">
        <div>
            <h1 class="text-3xl font-bold mb-2">Dashboard</h1>
            <p class="text-muted-foreground">
                Your accounts and latest balances
            </p>
        </div>
        <div class="flex gap-2">
            <Button variant="outline" onclick={openAddInstitution}
                >+ Add Institution</Button
            >
            <Button onclick={openAddAccount}>+ Add Account</Button>
        </div>
    </div>

    {#if error}
        <div class="bg-red-50 text-red-700 p-4 rounded mb-6">{error}</div>
    {/if}

    {#if !loading && accountsWithInstitutionName.length > 0}
        <div class="mb-8">
            {#key chartRefreshKey}
                <StackedBalanceChart />
            {/key}
        </div>
    {/if}

    {#if loading}
        <div class="text-center py-12 text-gray-600">Loading dashboard...</div>
    {:else if accountsWithInstitutionName.length === 0}
        <div class="text-center py-12 text-muted-foreground">
            No accounts yet. Add an institution and account to get started.
        </div>
    {:else}
        <div
            class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
        >
            {#each accountsWithInstitutionName as account (account.account_id)}
                <AccountBalanceCard
                    {account}
                    latestBalance={latestBalanceByAccountId[
                        account.account_id
                    ] ?? null}
                    balances={balancesByAccountId[account.account_id] ?? []}
                    onCreateBalance={handleCreateBalance}
                />
            {/each}
        </div>
    {/if}
</div>

{#key institutionsRefreshKey}
    <AddEditAccountDialog
        open={showAddAccount}
        editingAccount={null}
        loading={accountFormLoading}
        error={accountFormError}
        fieldErrors={accountFieldErrors}
        onOpenChange={(open) => {
            if (!open) showAddAccount = false;
        }}
        onSubmit={handleCreateAccount}
    />
{/key}

<AddEditInstitutionDialog
    open={showAddInstitution}
    editingInstitution={null}
    loading={institutionFormLoading}
    error={institutionFormError}
    fieldErrors={institutionFieldErrors}
    onOpenChange={(open) => {
        if (!open) showAddInstitution = false;
    }}
    onSubmit={handleCreateInstitution}
/>
