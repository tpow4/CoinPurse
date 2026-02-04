<script lang="ts">
    import type { Category } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import PencilIcon from '@lucide/svelte/icons/pencil';
    import TrashIcon from '@lucide/svelte/icons/trash-2';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        category: Category;
        onEdit?: (category: Category) => void;
        onDelete?: (category: Category) => void;
    }

    let { category, onEdit, onDelete }: Props = $props();
</script>

<div class="flex gap-1 justify-end">
    <Button
        variant="ghost"
        size="sm"
        disabled={!category.is_active}
        onclick={() => onEdit?.(category)}
        title={m.cat_action_edit()}
        aria-label={m.cat_action_edit()}
    >
        <PencilIcon class="size-4" />
    </Button>
    <Button
        variant="ghost"
        size="sm"
        disabled={!category.is_active}
        onclick={() => onDelete?.(category)}
        title={m.cat_action_delete()}
        aria-label={m.cat_action_delete()}
    >
        <TrashIcon class="size-4" />
    </Button>
</div>
