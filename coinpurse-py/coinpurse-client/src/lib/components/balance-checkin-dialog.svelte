<script lang="ts">
    import type { AccountDueForCheckin } from '$lib/types';
    import * as Dialog from '$lib/components/ui/dialog';
    import * as Field from '$lib/components/ui/field';
    import * as Card from '$lib/components/ui/card';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import * as m from '$lib/paraglide/messages';
    import { parseCentsCurrency } from '$lib/format';
    import { balancesApi } from '$lib/api/balances';

    interface Props {
        open: boolean;
        accounts: AccountDueForCheckin[];
        onOpenChange: (open: boolean) => void;
        onSuccess: () => void;
    }

    let { open, accounts, onOpenChange, onSuccess }: Props = $props();

    let balanceDate = $state('');
    let balanceValues: Record<number, string> = $state({});
    let balanceErrors: Record<number, string> = $state({});
    let saving = $state(false);
    let submitError = $state('');

    function todayIsoDate(): string {
        return new Date().toISOString().slice(0, 10);
    }

    // Group accounts by institution
    const grouped = $derived(Map.groupBy(accounts, (a) => a.institution_name));

    // Count how many inputs have a value
    const filledCount = $derived(
        Object.values(balanceValues).filter((v) => v.trim() !== '').length
    );

    // Reset form when dialog opens
    $effect(() => {
        if (!open) return;
        balanceDate = todayIsoDate();
        balanceValues = {};
        balanceErrors = {};
        saving = false;
        submitError = '';
    });

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        submitError = '';

        // Validate each filled input
        const newErrors: Record<number, string> = {};
        const entries: {
            account_id: number;
            balance_date: string;
            balance: number;
        }[] = [];

        for (const [accountId, value] of Object.entries(balanceValues)) {
            const trimmed = value.trim();
            if (!trimmed) continue;

            const cents = parseCentsCurrency(trimmed);
            if (cents === null) {
                newErrors[Number(accountId)] = m.balance_validation_invalid();
            } else {
                entries.push({
                    account_id: Number(accountId),
                    balance_date: balanceDate,
                    balance: cents,
                });
            }
        }

        if (Object.keys(newErrors).length > 0) {
            balanceErrors = newErrors;
            return;
        }

        if (entries.length === 0) return;

        saving = true;
        try {
            await Promise.all(
                entries.map((entry) =>
                    balancesApi.createBatch({
                        account_id: entry.account_id,
                        balances: [
                            {
                                balance_date: entry.balance_date,
                                balance: entry.balance,
                            },
                        ],
                    })
                )
            );
            onSuccess();
            onOpenChange(false);
        } catch {
            submitError = m.checkin_error();
        } finally {
            saving = false;
        }
    }
</script>

<Dialog.Root {open} {onOpenChange}>
    <Dialog.Content class="sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <Dialog.Header>
            <Dialog.Title>{m.checkin_dialog_title()}</Dialog.Title>
            <Dialog.Description
                >{m.checkin_dialog_description()}</Dialog.Description
            >
        </Dialog.Header>

        <form onsubmit={handleSubmit}>
            <div class="space-y-4">
                {#if submitError}
                    <div class="bg-red-50 text-red-700 p-4 rounded">
                        {submitError}
                    </div>
                {/if}

                <Field.Field>
                    <Field.Label for="checkin-date"
                        >{m.balance_field_date()}</Field.Label
                    >
                    <Input
                        id="checkin-date"
                        type="date"
                        bind:value={balanceDate}
                    />
                </Field.Field>

                {#each grouped as [institutionName, institutionAccounts]}
                    <Card.Root>
                        <Card.Header>
                            <Card.Title>{institutionName}</Card.Title>
                        </Card.Header>
                        <Card.Content class="space-y-1">
                            {#each institutionAccounts as account}
                                {@const hasError =
                                    balanceErrors[account.account_id]}
                                <Field.Field
                                    data-invalid={hasError ? true : undefined}
                                >
                                    <Field.Label
                                        for="checkin-{account.account_id}"
                                    >
                                        {account.account_name}
                                    </Field.Label>
                                    <Input
                                        id="checkin-{account.account_id}"
                                        inputmode="decimal"
                                        placeholder={m.balance_field_balance_placeholder()}
                                        value={balanceValues[
                                            account.account_id
                                        ] ?? ''}
                                        oninput={(e) => {
                                            balanceValues[account.account_id] =
                                                e.currentTarget.value;
                                            balanceErrors[account.account_id] =
                                                '';
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
                        </Card.Content>
                    </Card.Root>
                {/each}

                <Dialog.Footer>
                    <Button
                        type="button"
                        variant="outline"
                        onclick={() => onOpenChange(false)}
                        disabled={saving}
                    >
                        {m.btn_cancel()}
                    </Button>
                    <Button
                        type="submit"
                        disabled={saving || filledCount === 0}
                    >
                        {#if saving}
                            {m.balance_btn_saving()}
                        {:else if filledCount === 0}
                            {m.checkin_btn_save_count({ count: 0 })}
                        {:else}
                            {m.checkin_btn_save_count({ count: filledCount })}
                        {/if}
                    </Button>
                </Dialog.Footer>
            </div>
        </form>
    </Dialog.Content>
</Dialog.Root>
