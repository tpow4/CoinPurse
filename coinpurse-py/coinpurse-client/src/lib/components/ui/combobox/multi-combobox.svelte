<script lang="ts">
    import * as Popover from '$lib/components/ui/popover';
    import * as Command from '$lib/components/ui/command';
    import { buttonVariants } from '$lib/components/ui/button';
    import { cn } from '$lib/utils.js';
    import CheckIcon from '@lucide/svelte/icons/check';
    import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';

    export type ComboboxItem = {
        value: string;
        label: string;
        keywords?: string[];
    };

    interface Props {
        items: ComboboxItem[];
        values?: string[];
        open?: boolean;
        placeholder?: string;
        searchPlaceholder?: string;
        emptyText?: string;
        disabled?: boolean;
        id?: string;
        ariaInvalid?: boolean;
        class?: string;
        contentClass?: string;
        showSelectAll?: boolean;
        showSelectNone?: boolean;
        selectAllLabel?: string;
        selectNoneLabel?: string;
    }

    let {
        items,
        values = $bindable([]),
        open = $bindable(false),
        placeholder = 'Select...',
        searchPlaceholder = 'Search...',
        emptyText = 'No results found.',
        disabled = false,
        id,
        ariaInvalid = false,
        class: className,
        contentClass,
        showSelectAll = false,
        showSelectNone = false,
        selectAllLabel = 'Select all',
        selectNoneLabel = 'Select none',
    }: Props = $props();

    const selectedLabels = $derived(() => {
        const selected = items.filter((item) => values.includes(item.value));
        if (selected.length === 0) return '';
        if (selected.length <= 2)
            return selected.map((s) => s.label).join(', ');
        return `${selected.length} selected`;
    });

    function handleSelect(item: ComboboxItem) {
        if (disabled) return;
        if (values.includes(item.value)) {
            values = values.filter((v) => v !== item.value);
        } else {
            values = [...values, item.value];
        }
    }

    function handleSelectAll() {
        if (disabled) return;
        values = items.map((item) => item.value);
    }

    function handleSelectNone() {
        if (disabled) return;
        values = [];
    }
</script>

<Popover.Root bind:open>
    <Popover.Trigger
        {id}
        {disabled}
        role="combobox"
        aria-expanded={open}
        aria-invalid={ariaInvalid ? true : undefined}
        class={cn(
            buttonVariants({ variant: 'outline' }),
            'w-full justify-between',
            className
        )}
    >
        <span class="truncate">{selectedLabels() || placeholder}</span>
        <ChevronsUpDownIcon class="ml-2 size-4 shrink-0 opacity-50" />
    </Popover.Trigger>

    <Popover.Content
        align="start"
        class={cn(
            'w-auto min-w-[max(var(--bits-popover-anchor-width),18rem)] max-w-[min(24rem,calc(100vw-2rem))] p-0',
            contentClass
        )}
    >
        <Command.Root>
            <Command.Input placeholder={searchPlaceholder} />
            <Command.List>
                <Command.Empty>{emptyText}</Command.Empty>
                {#if showSelectAll || showSelectNone}
                    <div
                        class="flex items-center gap-2 border-b px-3 py-2 whitespace-nowrap"
                    >
                        {#if showSelectAll}
                            <button
                                type="button"
                                class="text-muted-foreground hover:text-foreground text-sm"
                                onclick={handleSelectAll}
                            >
                                {selectAllLabel}
                            </button>
                        {/if}
                        {#if showSelectAll && showSelectNone}
                            <span class="text-muted-foreground text-sm">|</span>
                        {/if}
                        {#if showSelectNone}
                            <button
                                type="button"
                                class="text-muted-foreground hover:text-foreground text-sm"
                                onclick={handleSelectNone}
                            >
                                {selectNoneLabel}
                            </button>
                        {/if}
                    </div>
                {/if}
                <Command.Group>
                    {#each items as item (item.value)}
                        <Command.Item
                            value={`${item.label} ${item.value}`}
                            keywords={[item.value, ...(item.keywords ?? [])]}
                            onSelect={() => handleSelect(item)}
                        >
                            <CheckIcon
                                class={cn(
                                    'mr-2 size-4',
                                    values.includes(item.value)
                                        ? 'opacity-100'
                                        : 'opacity-0'
                                )}
                            />
                            {item.label}
                        </Command.Item>
                    {/each}
                </Command.Group>
            </Command.List>
        </Command.Root>
    </Popover.Content>
</Popover.Root>
