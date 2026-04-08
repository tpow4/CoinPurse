<script lang="ts">
    import {
        type Account,
        type Institution,
        type ImportTemplate,
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
    import { importApi } from '$lib/api/import';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        open: boolean;
        editingAccount?: Account | null;
        loading?: boolean;
        error?: string;
        fieldErrors?: {
            account_name?: string;
            institution_id?: string;
            template_id?: string;
            account_type?: string;
            tax_treatment?: string;
            last_4_digits?: string;
        };
        onOpenChange: (open: boolean) => void;
        onSubmit: (data: {
            account_name: string;
            institution_id: number;
            template_id?: number | null;
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
        template_id: string;
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
        template_id: '',
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

    let importTemplates = $state<ImportTemplate[]>([]);
    let loadingTemplates = $state(false);
    let templatesLoaded = $state(false);

    let formData = $state<FormData>({ ...defaultFormData });

    function resetFormData() {
        Object.assign(formData, defaultFormData);
    }

    function populateFormData(account: Account) {
        Object.assign(formData, {
            account_name: account.account_name,
            institution_id: String(account.institution_id),
            template_id: account.template_id ? String(account.template_id) : '',
            account_type: account.account_type,
            tax_treatment: account.tax_treatment,
            last_4_digits: account.last_4_digits,
            tracks_transactions: account.tracks_transactions,
            tracks_balances: account.tracks_balances,
            display_order: account.display_order,
        } satisfies FormData);
    }

    // Account type options
    const accountTypes = $derived([
        { value: AccountTypeEnum.BANKING, label: m.account_type_banking() },
        { value: AccountTypeEnum.TREASURY, label: m.account_type_treasury() },
        { value: AccountTypeEnum.CREDIT_CARD, label: m.account_type_credit_card() },
        { value: AccountTypeEnum.INVESTMENT, label: m.account_type_investment() },
    ]);

    const taxTreatments = $derived([
        { value: TaxTreatmentType.TAXABLE, label: m.tax_taxable() },
        { value: TaxTreatmentType.TAX_DEFERRED, label: m.tax_deferred() },
        { value: TaxTreatmentType.TAX_FREE, label: m.tax_free() },
        { value: TaxTreatmentType.TRIPLE_TAX_FREE, label: m.tax_triple_free() },
        { value: TaxTreatmentType.NOT_APPLICABLE, label: m.tax_not_applicable() },
    ]);

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

    // Lazy-load import templates when dialog opens
    $effect(() => {
        if (!open || templatesLoaded || loadingTemplates) return;

        loadingTemplates = true;
        importApi
            .getTemplates(false) // active only
            .then((res) => {
                importTemplates = res;
                templatesLoaded = true;
            })
            .catch((e) => {
                console.error('Failed to load import templates:', e);
            })
            .finally(() => {
                loadingTemplates = false;
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

    const templateItems = $derived(
        importTemplates.map((template) => ({
            value: String(template.template_id),
            label: template.template_name,
        }))
    );

    // Disable template dropdown until institution is selected
    const templateDisabled = $derived(!formData.institution_id);

    function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        if (loading) return;
        onSubmit({
            account_name: formData.account_name,
            institution_id: Number(formData.institution_id),
            template_id: formData.template_id ? Number(formData.template_id) : null,
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
                {editingAccount !== null ? m.acct_dialog_title_edit() : m.acct_dialog_title_add()}
            </Dialog.Title>
            <Dialog.Description>
                {editingAccount !== null
                    ? m.acct_dialog_desc_edit()
                    : m.acct_dialog_desc_add()}
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
                    <Field.Label for="account_name">{m.acct_field_name()}</Field.Label>
                    <Input
                        type="text"
                        id="account_name"
                        bind:value={formData.account_name}
                        placeholder={m.acct_field_name_placeholder()}
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
                    <Field.Label for="institution_id">{m.acct_field_institution()}</Field.Label>
                    <Combobox
                        id="institution"
                        items={institutionItems}
                        bind:value={formData.institution_id}
                        placeholder={m.acct_field_institution_placeholder()}
                        searchPlaceholder={m.acct_field_institution_search()}
                        ariaInvalid={fieldErrors.institution_id ? true : false}
                    />
                    {#if fieldErrors.institution_id}
                        <Field.Error>{fieldErrors.institution_id}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Import Template -->
                <Field.Field
                    data-invalid={fieldErrors.template_id ? true : undefined}
                >
                    <Field.Label for="template_id">{m.acct_field_template()}</Field.Label>
                    <Combobox
                        id="template_id"
                        items={templateItems}
                        bind:value={formData.template_id}
                        placeholder={m.acct_field_template_placeholder()}
                        searchPlaceholder={m.acct_field_template_search()}
                        ariaInvalid={fieldErrors.template_id ? true : false}
                        disabled={templateDisabled}
                    />
                    {#if fieldErrors.template_id}
                        <Field.Error>{fieldErrors.template_id}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Account Type -->
                <Field.Field
                    data-invalid={fieldErrors.account_type ? true : undefined}
                >
                    <Field.Label for="account_type">{m.acct_field_type()}</Field.Label>
                    <Combobox
                        id="account_type"
                        items={accountTypes}
                        bind:value={formData.account_type}
                        placeholder={m.acct_field_type_placeholder()}
                        searchPlaceholder={m.acct_field_type_search()}
                        ariaInvalid={fieldErrors.account_type ? true : false}
                    />
                    {#if fieldErrors.account_type}
                        <Field.Error>{fieldErrors.account_type}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Tax Treatment -->
                <Field.Field>
                    <Field.Label for="tax_treatment">{m.acct_field_tax()}</Field.Label>
                    <Combobox
                        id="tax_treatment"
                        items={taxTreatments}
                        bind:value={formData.tax_treatment}
                        placeholder={m.acct_field_tax_placeholder()}
                        searchPlaceholder={m.acct_field_tax_search()}
                    />
                    {#if fieldErrors.tax_treatment}
                        <Field.Error>{fieldErrors.tax_treatment}</Field.Error>
                    {/if}
                </Field.Field>

                <!-- Last 4 Digits -->
                <Field.Field
                    data-invalid={fieldErrors.last_4_digits ? true : undefined}
                >
                    <Field.Label for="last_4_digits">{m.acct_field_last4()}</Field.Label>
                    <Input
                        type="text"
                        id="last_4_digits"
                        bind:value={formData.last_4_digits}
                        placeholder={m.acct_field_last4_placeholder()}
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
                    <Field.Label for="display_order">{m.acct_field_display_order()}</Field.Label>
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
                        {m.acct_field_tracks_transactions()}
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
                        {m.acct_field_tracks_balances()}
                    </Label>
                </div>
            </div>

            <Dialog.Footer class="mt-6">
                <Button
                    type="button"
                    variant="outline"
                    onclick={() => onOpenChange(false)}
                >
                    {m.btn_cancel()}
                </Button>
                <Button type="submit" disabled={loading}>
                    {loading
                        ? m.btn_saving()
                        : editingAccount !== null
                          ? m.btn_update()
                          : m.btn_create()}
                </Button>
            </Dialog.Footer>
        </form>
    </Dialog.Content>
</Dialog.Root>
