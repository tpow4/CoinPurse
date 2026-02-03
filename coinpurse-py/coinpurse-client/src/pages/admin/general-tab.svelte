<script lang="ts">
    import * as m from '$lib/paraglide/messages';
    import { getLocale, setLocale, locales } from '$lib/paraglide/runtime';
    import type { Locale } from '$lib/paraglide/runtime';
    import { getCurrency, setCurrency, SUPPORTED_CURRENCIES } from '$lib/format';
    import * as Card from '$lib/components/ui/card';
    import * as Select from '$lib/components/ui/select';

    const localeLabels: Record<string, string> = {
        en: 'English',
        es: 'Español',
        de: 'Deutsch',
    };

    let currentLocale = $state(getLocale());
    let currentCurrency = $state(getCurrency());
    let savedMessage = $state('');
    let savedTimeout: ReturnType<typeof setTimeout> | undefined;

    function handleLocaleChange(value: string | undefined) {
        if (!value || value === currentLocale) return;
        currentLocale = value;
        setLocale(value as Locale);
    }

    function handleCurrencyChange(value: string | undefined) {
        if (!value || value === currentCurrency) return;
        currentCurrency = value;
        setCurrency(value);
        showSaved();
    }

    function showSaved() {
        savedMessage = m.general_saved();
        if (savedTimeout) clearTimeout(savedTimeout);
        savedTimeout = setTimeout(() => {
            savedMessage = '';
        }, 2000);
    }
</script>

<div class="grid gap-6 max-w-2xl">
    <Card.Root>
        <Card.Header>
            <Card.Title>{m.general_locale_label()}</Card.Title>
            <Card.Description>{m.general_locale_description()}</Card.Description>
        </Card.Header>
        <Card.Content>
            <Select.Root type="single" value={currentLocale} onValueChange={handleLocaleChange}>
                <Select.Trigger class="w-[240px]">
                    {localeLabels[currentLocale] ?? currentLocale}
                </Select.Trigger>
                <Select.Content>
                    {#each locales as locale}
                        <Select.Item value={locale} label={localeLabels[locale] ?? locale} />
                    {/each}
                </Select.Content>
            </Select.Root>
        </Card.Content>
    </Card.Root>

    <Card.Root>
        <Card.Header>
            <Card.Title>{m.general_currency_label()}</Card.Title>
            <Card.Description>{m.general_currency_description()}</Card.Description>
        </Card.Header>
        <Card.Content>
            <div class="flex items-center gap-3">
                <Select.Root type="single" value={currentCurrency} onValueChange={handleCurrencyChange}>
                    <Select.Trigger class="w-[280px]">
                        {SUPPORTED_CURRENCIES.find((c) => c.code === currentCurrency)?.label ?? currentCurrency}
                    </Select.Trigger>
                    <Select.Content>
                        {#each SUPPORTED_CURRENCIES as currency}
                            <Select.Item value={currency.code} label={currency.label} />
                        {/each}
                    </Select.Content>
                </Select.Root>
                {#if savedMessage}
                    <span class="text-sm text-muted-foreground animate-in fade-in">{savedMessage}</span>
                {/if}
            </div>
        </Card.Content>
    </Card.Root>
</div>
