<script lang="ts">
    import type {
        AccountBalance,
        BalanceCreate,
        BalanceBatchCreate,
    } from '$lib/types';
    import * as Dialog from '$lib/components/ui/dialog';
    import * as Field from '$lib/components/ui/field';
    import * as Tabs from '$lib/components/ui/tabs';
    import * as Select from '$lib/components/ui/select';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import { TriangleAlert } from '@lucide/svelte';
    import * as m from '$lib/paraglide/messages';
    import { formatDate } from '$lib/format';

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
        onSubmit: (
            data: BalanceCreate
        ) => Promise<AccountBalance | void> | AccountBalance | void;
        onSubmitBatch: (data: BalanceBatchCreate) => Promise<void>;
        accountId: number;
        defaultBalanceDate?: string;
        existingBalances: AccountBalance[];
    }

    let {
        open = false,
        accountName,
        accountId,
        defaultBalanceDate,
        loading = false,
        error = '',
        fieldErrors = {},
        onOpenChange,
        onSubmit,
        onSubmitBatch,
        existingBalances = [],
    }: Props = $props();

    // Tab state
    let activeTab = $state<string>('single');

    // Single entry form state
    type FormData = {
        balance: string;
        balance_date: string;
    };

    let localFieldErrors = $state<{ balance?: string }>({});
    let formData = $state<FormData>({ balance: '', balance_date: '' });

    // Yearly entry form state
    const currentYear = new Date().getFullYear();
    let selectedYear = $state(currentYear);
    let selectedDay = $state(1);
    let monthValues = $state<Record<number, string>>({});
    let monthErrors = $state<Record<number, string>>({});

    // Month names derived from locale-aware formatting
    function getMonthName(month: number): string {
        const date = new Date(2000, month - 1, 1);
        return formatDate(date, { month: 'long', year: undefined, day: undefined });
    }

    // Generate year options (current year +/- 10 years)
    const yearOptions = Array.from(
        { length: 21 },
        (_, i) => currentYear - 10 + i
    );

    // Generate day options (1-28 to avoid invalid dates)
    const dayOptions = Array.from({ length: 28 }, (_, i) => i + 1);

    function todayIsoDate(): string {
        return new Date().toISOString().slice(0, 10);
    }

    function initialBalanceDate(): string {
        return defaultBalanceDate ?? todayIsoDate();
    }

    function parseMoneyToCents(input: string): number | null {
        const trimmed = input.trim().replaceAll(',', '');
        if (!trimmed) return null;

        const match = trimmed.match(/^(-)?(\d+)(?:\.(\d{0,2}))?$/);
        if (!match) return null;

        const sign = match[1] ? -1 : 1;
        const dollarsPart = match[2] ?? '0';
        const centsPart = (match[3] ?? '').padEnd(2, '0');
        const dollars = Number(dollarsPart);
        const cents = Number(centsPart || '0');

        if (!Number.isFinite(dollars) || !Number.isFinite(cents)) return null;
        return sign * (dollars * 100 + cents);
    }

    function formatCentsToMoney(cents: number): string {
        const dollars = Math.abs(cents) / 100;
        const sign = cents < 0 ? '-' : '';
        return (
            sign +
            dollars.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            })
        );
    }

    function getDateForMonth(month: number): string {
        // month is 1-12
        const paddedMonth = String(month).padStart(2, '0');
        const paddedDay = String(selectedDay).padStart(2, '0');
        return `${selectedYear}-${paddedMonth}-${paddedDay}`;
    }

    // Check if a month has an existing balance for the selected year/day
    function getExistingBalanceForMonth(
        month: number
    ): AccountBalance | undefined {
        const targetDate = getDateForMonth(month);
        return existingBalances.find((b) => b.balance_date === targetDate);
    }

    // Count how many months have values entered
    const entryCount = $derived(
        Object.values(monthValues).filter((v) => v.trim() !== '').length
    );

    // Reset form when dialog opens
    $effect(() => {
        if (!open) return;
        // Set default tab based on whether account has existing balances
        activeTab = existingBalances.length === 0 ? 'yearly' : 'single';
        // Reset single entry form
        formData.balance = '';
        formData.balance_date = initialBalanceDate();
        localFieldErrors = {};
        // Reset yearly entry form
        selectedYear = currentYear;
        selectedDay = 1;
        monthValues = {};
        monthErrors = {};
    });

    // Pre-fill existing balances when year/day changes
    $effect(() => {
        if (!open) return;
        const newValues: Record<number, string> = {};
        for (let month = 1; month <= 12; month++) {
            const existing = getExistingBalanceForMonth(month);
            if (existing) {
                newValues[month] = formatCentsToMoney(existing.balance);
            }
        }
        monthValues = newValues;
        monthErrors = {};
    });

    async function handleSingleSubmit(e: SubmitEvent) {
        e.preventDefault();
        const cents = parseMoneyToCents(formData.balance);
        if (cents === null) {
            localFieldErrors = {
                balance: m.balance_validation_number(),
            };
            return;
        }
        await onSubmit({
            account_id: accountId,
            balance_date: formData.balance_date,
            balance: cents,
        });
    }

    async function handleYearlySubmit(e: SubmitEvent) {
        e.preventDefault();

        // Validate and collect entries
        const entries: { balance_date: string; balance: number }[] = [];
        const newErrors: Record<number, string> = {};

        for (let month = 1; month <= 12; month++) {
            const value = monthValues[month]?.trim();
            if (!value) continue;

            const cents = parseMoneyToCents(value);
            if (cents === null) {
                newErrors[month] = m.balance_validation_invalid();
            } else {
                entries.push({
                    balance_date: getDateForMonth(month),
                    balance: cents,
                });
            }
        }

        if (Object.keys(newErrors).length > 0) {
            monthErrors = newErrors;
            return;
        }

        if (entries.length === 0) {
            return;
        }

        await onSubmitBatch({
            account_id: accountId,
            balances: entries,
        });
    }
</script>

<Dialog.Root {open} {onOpenChange}>
    <Dialog.Content class="sm:max-w-135">
        <Dialog.Header>
            <Dialog.Title>{m.balance_dialog_title()}</Dialog.Title>
            <Dialog.Description
                >{m.balance_dialog_description({ accountName })}</Dialog.Description
            >
        </Dialog.Header>

        <Tabs.Root
            value={activeTab}
            onValueChange={(v) => (activeTab = v ?? 'single')}
        >
            <Tabs.List class="mb-4">
                <Tabs.Trigger value="single">{m.balance_tab_single()}</Tabs.Trigger>
                <Tabs.Trigger value="yearly">{m.balance_tab_yearly()}</Tabs.Trigger>
            </Tabs.List>

            <Tabs.Content value="single">
                <form onsubmit={handleSingleSubmit}>
                    <div class="space-y-4">
                        {#if error && activeTab === 'single'}
                            <div class="bg-red-50 text-red-700 p-4 rounded">
                                {error}
                            </div>
                        {/if}

                        <Field.Field
                            data-invalid={fieldErrors.balance ||
                            localFieldErrors.balance
                                ? true
                                : undefined}
                        >
                            <Field.Label for="balance">{m.balance_field_balance()}</Field.Label>
                            <Input
                                id="balance"
                                inputmode="decimal"
                                placeholder={m.balance_field_balance_placeholder()}
                                bind:value={formData.balance}
                                aria-invalid={fieldErrors.balance ||
                                localFieldErrors.balance
                                    ? true
                                    : undefined}
                                oninput={() => {
                                    localFieldErrors.balance = '';
                                }}
                            />
                            {#if fieldErrors.balance || localFieldErrors.balance}
                                <Field.Error
                                    >{fieldErrors.balance ??
                                        localFieldErrors.balance}</Field.Error
                                >
                            {/if}
                        </Field.Field>

                        <Field.Field
                            data-invalid={fieldErrors.balance_date
                                ? true
                                : undefined}
                        >
                            <Field.Label for="balance_date">{m.balance_field_date()}</Field.Label>
                            <Input
                                id="balance_date"
                                type="date"
                                bind:value={formData.balance_date}
                                aria-invalid={fieldErrors.balance_date
                                    ? true
                                    : undefined}
                            />
                            {#if fieldErrors.balance_date}
                                <Field.Error
                                    >{fieldErrors.balance_date}</Field.Error
                                >
                            {/if}
                        </Field.Field>

                        <div class="flex justify-end gap-2 pt-2">
                            <Button
                                type="button"
                                variant="outline"
                                onclick={() => onOpenChange(false)}
                                disabled={loading}
                            >
                                {m.balance_btn_cancel()}
                            </Button>
                            <Button type="submit" disabled={loading}>
                                {loading ? m.balance_btn_saving() : m.balance_btn_save()}
                            </Button>
                        </div>
                    </div>
                </form>
            </Tabs.Content>

            <Tabs.Content value="yearly">
                <form onsubmit={handleYearlySubmit}>
                    <div class="space-y-4">
                        {#if error && activeTab === 'yearly'}
                            <div class="bg-red-50 text-red-700 p-4 rounded">
                                {error}
                            </div>
                        {/if}

                        <div class="flex gap-4">
                            <Field.Field class="flex-1">
                                <Field.Label for="year">{m.balance_field_year()}</Field.Label>
                                <Select.Root
                                    type="single"
                                    value={String(selectedYear)}
                                    onValueChange={(v) =>
                                        (selectedYear = Number(v))}
                                >
                                    <Select.Trigger id="year" class="w-full">
                                        {selectedYear}
                                    </Select.Trigger>
                                    <Select.Content>
                                        {#each yearOptions as year}
                                            <Select.Item value={String(year)}
                                                >{year}</Select.Item
                                            >
                                        {/each}
                                    </Select.Content>
                                </Select.Root>
                            </Field.Field>

                            <Field.Field class="flex-1">
                                <Field.Label for="day">{m.balance_field_day()}</Field.Label
                                >
                                <Select.Root
                                    type="single"
                                    value={String(selectedDay)}
                                    onValueChange={(v) =>
                                        (selectedDay = Number(v))}
                                >
                                    <Select.Trigger id="day" class="w-full">
                                        {selectedDay}
                                    </Select.Trigger>
                                    <Select.Content>
                                        {#each dayOptions as day}
                                            <Select.Item value={String(day)}
                                                >{day}</Select.Item
                                            >
                                        {/each}
                                    </Select.Content>
                                </Select.Root>
                            </Field.Field>
                        </div>

                        <div
                            class="grid grid-cols-2 gap-x-4 gap-y-2 max-h-75 overflow-y-auto pr-2"
                        >
                            {#each { length: 12 } as _, index}
                                {@const month = index + 1}
                                {@const monthName = getMonthName(month)}
                                {@const existing =
                                    getExistingBalanceForMonth(month)}
                                {@const hasError = monthErrors[month]}
                                <Field.Field
                                    data-invalid={hasError ? true : undefined}
                                >
                                    <Field.Label
                                        for="month-{month}"
                                        class="flex items-center gap-1"
                                    >
                                        {monthName}
                                        {#if existing}
                                            <TriangleAlert
                                                class="h-3 w-3 text-amber-500"
                                            />
                                        {/if}
                                    </Field.Label>
                                    <Input
                                        id="month-{month}"
                                        inputmode="decimal"
                                        placeholder="0.00"
                                        value={monthValues[month] ?? ''}
                                        oninput={(e) => {
                                            monthValues[month] =
                                                e.currentTarget.value;
                                            monthErrors[month] = '';
                                        }}
                                        aria-invalid={hasError
                                            ? true
                                            : undefined}
                                    />
                                    {#if hasError}
                                        <Field.Error>{hasError}</Field.Error>
                                    {/if}
                                </Field.Field>
                            {/each}
                        </div>

                        <div class="flex justify-end gap-2 pt-2">
                            <Button
                                type="button"
                                variant="outline"
                                onclick={() => onOpenChange(false)}
                                disabled={loading}
                            >
                                {m.balance_btn_cancel()}
                            </Button>
                            <Button
                                type="submit"
                                disabled={loading || entryCount === 0}
                            >
                                {#if loading}
                                    {m.balance_btn_saving()}
                                {:else if entryCount === 0}
                                    {m.balance_btn_save()}
                                {:else}
                                    {m.balance_btn_save_count({ count: entryCount })}
                                {/if}
                            </Button>
                        </div>
                    </div>
                </form>
            </Tabs.Content>
        </Tabs.Root>
    </Dialog.Content>
</Dialog.Root>
