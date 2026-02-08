<script lang="ts">
    import { onDestroy } from 'svelte';
    import * as m from '$lib/paraglide/messages';
    import { getLocale, setLocale, locales } from '$lib/paraglide/runtime';
    import type { Locale } from '$lib/paraglide/runtime';
    import {
        getCurrency,
        setCurrency,
        SUPPORTED_CURRENCIES,
    } from '$lib/format';
    import * as Card from '$lib/components/ui/card';
    import * as Select from '$lib/components/ui/select';
    import { settingsApi } from '$lib/api/settings';

    const FREQUENCY_OPTIONS = [
        { value: '7', label: () => m.general_frequency_weekly() },
        { value: '14', label: () => m.general_frequency_biweekly() },
        { value: '30', label: () => m.general_frequency_monthly() },
        { value: '90', label: () => m.general_frequency_quarterly() },
    ];

    function localeLabel(locale: Locale): string {
        return m.locale_name({}, { locale });
    }

    let currentLocale: Locale = $state(getLocale());
    let currentCurrency = $state(getCurrency());
    let currentFrequency = $state('7');
    let currencySaved = $state('');
    let currencyTimeout: ReturnType<typeof setTimeout> | undefined;
    let frequencySaved = $state('');
    let frequencyTimeout: ReturnType<typeof setTimeout> | undefined;

    // Load current frequency setting on mount
    $effect(() => {
        settingsApi
            .getByKey('balance_checkin_frequency_days')
            .then((setting) => {
                currentFrequency = setting.setting_value;
            })
            .catch(() => {
                // Use default if setting doesn't exist yet
            });
    });

    function handleLocaleChange(value: string | undefined) {
        if (!value || value === currentLocale) return;
        const locale = value as Locale;
        currentLocale = locale;
        setLocale(locale);
    }

    function handleCurrencyChange(value: string | undefined) {
        if (!value || value === currentCurrency) return;
        currentCurrency = value;
        setCurrency(value);
        showCurrencySaved();
    }

    function handleFrequencyChange(value: string | undefined) {
        if (!value || value === currentFrequency) return;
        const previousFrequency = currentFrequency;
        currentFrequency = value;
        settingsApi
            .upsert('balance_checkin_frequency_days', { setting_value: value })
            .then(() => {
                showFrequencySaved();
            })
            .catch(() => {
                currentFrequency = previousFrequency;
            });
    }

    function showCurrencySaved() {
        currencySaved = m.general_saved();
        if (currencyTimeout) clearTimeout(currencyTimeout);
        currencyTimeout = setTimeout(() => { currencySaved = ''; }, 2000);
    }

    function showFrequencySaved() {
        frequencySaved = m.general_saved();
        if (frequencyTimeout) clearTimeout(frequencyTimeout);
        frequencyTimeout = setTimeout(() => { frequencySaved = ''; }, 2000);
    }

    onDestroy(() => {
        if (currencyTimeout) clearTimeout(currencyTimeout);
        if (frequencyTimeout) clearTimeout(frequencyTimeout);
    });
</script>

<div class="grid gap-6 max-w-2xl">
    <Card.Root>
        <Card.Header>
            <Card.Title>{m.general_locale_label()}</Card.Title>
            <Card.Description>{m.general_locale_description()}</Card.Description
            >
        </Card.Header>
        <Card.Content>
            <Select.Root
                type="single"
                value={currentLocale}
                onValueChange={handleLocaleChange}
            >
                <Select.Trigger class="w-60">
                    {localeLabel(currentLocale)}
                </Select.Trigger>
                <Select.Content>
                    {#each locales as locale}
                        <Select.Item
                            value={locale}
                            label={localeLabel(locale)}
                        />
                    {/each}
                </Select.Content>
            </Select.Root>
        </Card.Content>
    </Card.Root>

    <Card.Root>
        <Card.Header>
            <Card.Title>{m.general_currency_label()}</Card.Title>
            <Card.Description
                >{m.general_currency_description()}</Card.Description
            >
        </Card.Header>
        <Card.Content>
            <div class="flex items-center gap-3">
                <Select.Root
                    type="single"
                    value={currentCurrency}
                    onValueChange={handleCurrencyChange}
                >
                    <Select.Trigger class="w-70">
                        {SUPPORTED_CURRENCIES.find(
                            (c) => c.code === currentCurrency
                        )?.label ?? currentCurrency}
                    </Select.Trigger>
                    <Select.Content>
                        {#each SUPPORTED_CURRENCIES as currency}
                            <Select.Item
                                value={currency.code}
                                label={currency.label}
                            />
                        {/each}
                    </Select.Content>
                </Select.Root>
                {#if currencySaved}
                    <span
                        class="text-sm text-muted-foreground animate-in fade-in"
                        >{currencySaved}</span
                    >
                {/if}
            </div>
        </Card.Content>
    </Card.Root>

    <Card.Root>
        <Card.Header>
            <Card.Title>{m.general_frequency_label()}</Card.Title>
            <Card.Description
                >{m.general_frequency_description()}</Card.Description
            >
        </Card.Header>
        <Card.Content>
            <div class="flex items-center gap-3">
                <Select.Root
                    type="single"
                    value={currentFrequency}
                    onValueChange={handleFrequencyChange}
                >
                    <Select.Trigger class="w-60">
                        {FREQUENCY_OPTIONS.find(
                            (o) => o.value === currentFrequency
                        )?.label() ?? currentFrequency}
                    </Select.Trigger>
                    <Select.Content>
                        {#each FREQUENCY_OPTIONS as option}
                            <Select.Item
                                value={option.value}
                                label={option.label()}
                            />
                        {/each}
                    </Select.Content>
                </Select.Root>
                {#if frequencySaved}
                    <span
                        class="text-sm text-muted-foreground animate-in fade-in"
                        >{frequencySaved}</span
                    >
                {/if}
            </div>
        </Card.Content>
    </Card.Root>
</div>
