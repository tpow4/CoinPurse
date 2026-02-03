<script lang="ts">
    import {
        type Account,
        type Institution,
        type AccountType,
        TaxTreatmentType,
    } from '$lib/types';
    import { AccountType as AccountTypeEnum } from '$lib/types';
    import * as Dialog from '$lib/components/ui/dialog';
    import * as Field from '$lib/components/ui/field';
    import { Combobox } from '$lib/components/ui/combobox';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import { Checkbox } from '$lib/components/ui/checkbox';
    import { Label } from '$lib/components/ui/label';
    import { institutionsApi } from '$lib/api/institutions';

    interface Props {
        open: boolean;
        editingAccount?: Account | null;
        loading?: boolean;
        error?: string;
        fieldErrors?: {
            account_name?: string;
            institution_id?: string;
            account_type?: string;
            tax_treatment?: string;
            last_4_digits?: string;
        };
        onOpenChange: (open: boolean) => void;
        onSubmit: (data: {
            account_name: string;
            institution_id: number;
            account_type: AccountType;
            tax_treatment: TaxTreatmentType;
            last_4_digits: string;
            tracks_transactions: boolean;
            tracks_balances: boolean;
            display_order: number;
        }) => void;
    }

    let {
        open = false,
        editingAccount = null,
        loading = false,
        error = '',
        fieldErrors = {},
        onOpenChange,
        onSubmit,
    }: Props = $props();

    type FormData = {
        account_name: string;
        institution_id: string;
        account_type: AccountType;
        tax_treatment: TaxTreatmentType;
        last_4_digits: string;
        tracks_transactions: boolean;
        tracks_balances: boolean;
        display_order: number;
    };

    const defaultFormData: FormData = {
        account_name: '',
        institution_id: '',
        account_type: AccountTypeEnum.BANKING,
        tax_treatment: TaxTreatmentType.TAXABLE,
        last_4_digits: '',
        tracks_transactions: true,
        tracks_balances: true,
        display_order: 0,
    };

    let institutions = $state<Institution[]>([]);
    let loadingInstitutions = $state(false);
    let institutionsLoaded = $state(false);

    let formData = $state<FormData>({ ...defaultFormData });

    function resetFormData() {
        Object.assign(formData, defaultFormData);
    }

    function populateFormData(account: Account) {
        Object.assign(formData, {
            account_name: account.account_name,
            institution_id: String(account.institution_id),
            account_type: account.account_type,
            tax_treatment: account.tax_treatment,
            last_4_digits: account.last_4_digits,
            tracks_transactions: account.tracks_transactions,
            tracks_balances: account.tracks_balances,
            display_order: account.display_order,
        } satisfies FormData);
    }

    // Account type options
    const accountTypes = [
        { value: AccountTypeEnum.BANKING, label: 'Banking' },
        { value: AccountTypeEnum.TREASURY, label: 'Treasury' },
        { value: AccountTypeEnum.CREDIT_CARD, label: 'Credit Card' },
        { value: AccountTypeEnum.INVESTMENT, label: 'Investment' },
    ];

    const taxTreatments = [
        { value: TaxTreatmentType.TAXABLE, label: 'Taxable' },
        { value: TaxTreatmentType.TAX_DEFERRED, label: 'Tax-Deferred' },
        { value: TaxTreatmentType.TAX_FREE, label: 'Tax-Free' },
        { value: TaxTreatmentType.TRIPLE_TAX_FREE, label: 'Triple Tax-Free' },
        { value: TaxTreatmentType.NOT_APPLICABLE, label: 'Not Applicable' },
    ];

    // Lazy-load institutions when dialog opens
    $effect(() => {
        if (!open || institutionsLoaded || loadingInstitutions) return;

        loadingInstitutions = true;
        institutionsApi
            .getAll(false) // active only
            .then((res) => {
                institutions = res;
                institutionsLoaded = true;
            })
            .catch((e) => {
                console.error('Failed to load institutions:', e);
            })
            .finally(() => {
                loadingInstitutions = false;
            });
    });

    // (Re)initialize form when dialog opens (prevents stale values when re-opening "Add")
    $effect(() => {
        if (!open) return;
        if (editingAccount) populateFormData(editingAccount);
        else resetFormData();
    });

    // Also reset on close so the next open starts clean
    $effect(() => {
        if (open) return;
        resetFormData();
    });

    const institutionItems = $derived(
        institutions.map((institution) => ({
            value: String(institution.institution_id),
            label: institution.name,
        }))
    );

    function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        if (loading) return;
        onSubmit({
            account_name: formData.account_name,
            institution_id: Number(formData.institution_id),
            account_type: formData.account_type,
            tax_treatment: formData.tax_treatment,
            last_4_digits: formData.last_4_digits,
            tracks_transactions: formData.tracks_transactions,
            tracks_balances: formData.tracks_balances,
            display_order: formData.display_order,
        });
    }
</script>

<Dialog.Root {open} {onOpenChange}>
    <Dialog.Content class="sm:max-w-125 max-h-[90vh] overflow-y-auto">
        <Dialog.Header>
            <Dialog.Title>
                {editingAccount !== null ? 'Edit Account' : 'Add Account'}
            </Dialog.Title>
            <Dialog.Description>
                {editingAccount !== null
                    ? 'Update the account details below.'
                    : 'Add a new account to track transactions and balances.'}
            </Dialog.Description>
        </Dialog.Header>

        <form onsubmit={handleSubmit}>
            <div class="space-y-4">
                {#if error}
                    <div class="bg-red-50 text-red-700 p-4 rounded mb-4">
                        {error}
                    </div>
                {/if}

                <!-- Account Name -->
                <Field.Field
                    data-invalid={fieldErrors.account_name ? true : undefined}
                >
                    <Field.Label for="account_name">Account Name</Field.Label>
                    <Input
                        type="text"
                        id="account_name"
                        bind:value={formData.account_name}
                        placeholder="e.g., Primary Checking"
                        aria-invalid={fieldErrors.account_name
                            ? true
                            : undefined}
                    />
                    {#if fieldErrors.account_name}
                        <Field.Error>{fieldErrors.account_name}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Institution -->
                <Field.Field
                    data-invalid={fieldErrors.institution_id ? true : undefined}
                >
                    <Field.Label for="institution_id">Institution</Field.Label>
                    <Combobox
                        id="institution"
                        items={institutionItems}
                        bind:value={formData.institution_id}
                        placeholder="Select institution"
                        searchPlaceholder="Search institutions..."
                        ariaInvalid={fieldErrors.institution_id ? true : false}
                    />
                    {#if fieldErrors.institution_id}
                        <Field.Error>{fieldErrors.institution_id}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Account Type -->
                <Field.Field
                    data-invalid={fieldErrors.account_type ? true : undefined}
                >
                    <Field.Label for="account_type">Account Type</Field.Label>
                    <Combobox
                        id="account_type"
                        items={accountTypes}
                        bind:value={formData.account_type}
                        placeholder="Select account type"
                        searchPlaceholder="Search account types..."
                        ariaInvalid={fieldErrors.account_type ? true : false}
                    />
                    {#if fieldErrors.account_type}
                        <Field.Error>{fieldErrors.account_type}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Tax Treatment -->
                <Field.Field>
                    <Field.Label for="tax_treatment">Tax Treatment</Field.Label>
                    <Combobox
                        id="tax_treatment"
                        items={taxTreatments}
                        bind:value={formData.tax_treatment}
                        placeholder="Select tax treatment"
                        searchPlaceholder="Search tax treatments..."
                    />
                    {#if fieldErrors.tax_treatment}
                        <Field.Error>{fieldErrors.tax_treatment}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Last 4 Digits -->
                <Field.Field
                    data-invalid={fieldErrors.last_4_digits ? true : undefined}
                >
                    <Field.Label for="last_4_digits">Last 4 Digits</Field.Label>
                    <Input
                        type="text"
                        id="last_4_digits"
                        bind:value={formData.last_4_digits}
                        placeholder="1234"
                        maxlength={4}
                        aria-invalid={fieldErrors.last_4_digits
                            ? true
                            : undefined}
                    />
                    {#if fieldErrors.last_4_digits}
                        <Field.Error>{fieldErrors.last_4_digits}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Display Order -->
                <Field.Field>
                    <Field.Label for="display_order">Display Order</Field.Label>
                    <Input
                        type="number"
                        id="display_order"
                        bind:value={formData.display_order}
                        placeholder="0"
                    />
                </Field.Field>

                <!-- Tracks Transactions -->
                <div class="flex items-center gap-2">
                    <Checkbox
                        id="tracks_transactions"
                        checked={formData.tracks_transactions}
                        onCheckedChange={(checked) => {
                            formData.tracks_transactions = checked === true;
                        }}
                    />
                    <Label
                        for="tracks_transactions"
                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                        Track Transactions
                    </Label>
                </div>

                <!-- Tracks Balances -->
                <div class="flex items-center gap-2">
                    <Checkbox
                        id="tracks_balances"
                        checked={formData.tracks_balances}
                        onCheckedChange={(checked) => {
                            formData.tracks_balances = checked === true;
                        }}
                    />
                    <Label
                        for="tracks_balances"
                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                        Track Balances
                    </Label>
                </div>
            </div>

            <Dialog.Footer class="mt-6">
                <Button
                    type="button"
                    variant="outline"
                    onclick={() => onOpenChange(false)}
                >
                    Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                    {loading
                        ? 'Saving...'
                        : editingAccount !== null
                          ? 'Update'
                          : 'Create'}
                </Button>
            </Dialog.Footer>
        </form>
    </Dialog.Content>
</Dialog.Root>
