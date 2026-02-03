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
        value?: string;
        open?: boolean;
        placeholder?: string;
        searchPlaceholder?: string;
        emptyText?: string;
        disabled?: boolean;
        id?: string;
        ariaInvalid?: boolean;
        class?: string;
        contentClass?: string;
    }

    let {
        items,
        value = $bindable(''),
        open = $bindable(false),
        placeholder = 'Select…',
        searchPlaceholder = 'Search…',
        emptyText = 'No results found.',
        disabled = false,
        id,
        ariaInvalid = false,
        class: className,
        contentClass,
    }: Props = $props();

    const selectedItem = $derived(
        items.find((item) => item.value === value) ?? null
    );

    function handleSelect(item: ComboboxItem) {
        value = item.value;
        open = false;
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
        <span class="truncate"
            >{selectedItem ? selectedItem.label : placeholder}</span
        >
        <ChevronsUpDownIcon class="ml-2 size-4 shrink-0 opacity-50" />
    </Popover.Trigger>

    <Popover.Content
        align="start"
        class={cn('w-(--bits-popover-anchor-width) p-0', contentClass)}
    >
        <Command.Root>
            <Command.Input placeholder={searchPlaceholder} />
            <Command.List>
                <Command.Empty>{emptyText}</Command.Empty>
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
                                    item.value === value
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
