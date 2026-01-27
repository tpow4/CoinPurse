<script lang="ts">
    import type { Snippet } from 'svelte';
    import * as Collapsible from '$lib/components/ui/collapsible';
    import { ChevronDown, ChevronRight } from '@lucide/svelte';

    interface Props {
        title: string;
        count: number;
        variant?: 'default' | 'warning' | 'error';
        defaultOpen?: boolean;
        children: Snippet;
    }

    let {
        title,
        count,
        variant = 'default',
        defaultOpen = true,
        children,
    }: Props = $props();
    let open = $state(false);
    $effect(() => {
        open = defaultOpen;
    });

    const headerClass = $derived.by(() => {
        switch (variant) {
            case 'warning':
                return 'bg-amber-500/10 hover:bg-amber-500/20';
            case 'error':
                return 'bg-red-500/10 hover:bg-red-500/20';
            default:
                return 'bg-muted/50 hover:bg-muted';
        }
    });

    const countClass = $derived.by(() => {
        switch (variant) {
            case 'warning':
                return 'bg-amber-500/20 text-amber-700';
            case 'error':
                return 'bg-red-500/20 text-red-700';
            default:
                return 'bg-primary/10 text-primary';
        }
    });
</script>

<Collapsible.Root bind:open class="rounded-lg border">
    <Collapsible.Trigger
        class="flex w-full items-center justify-between rounded-t-lg px-4 py-3 text-left transition-colors {headerClass}"
        onclick={() => (open = !open)}
    >
        <div class="flex items-center gap-2">
            {#if open}
                <ChevronDown class="size-4" />
            {:else}
                <ChevronRight class="size-4" />
            {/if}
            <span class="font-medium">{title}</span>
        </div>
        <span class="rounded-full px-2 py-0.5 text-sm font-medium {countClass}">
            {count}
        </span>
    </Collapsible.Trigger>

    <Collapsible.Content class="border-t">
        {@render children()}
    </Collapsible.Content>
</Collapsible.Root>
