<script lang="ts">
    import type { Institution } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import PencilIcon from '@lucide/svelte/icons/pencil';
    import TrashIcon from '@lucide/svelte/icons/trash-2';

    interface Props {
        institution: Institution;
        onEdit?: (institution: Institution) => void;
        onDelete?: (institution: Institution) => void;
    }

    let { institution, onEdit, onDelete }: Props = $props();
</script>

<div class="flex gap-1 justify-end">
    <Button
        variant="ghost"
        size="sm"
        disabled={!institution.is_active}
        onclick={() => onEdit?.(institution)}
        title="Edit"
        aria-label="Edit Institution"
    >
        <PencilIcon class="size-4" />
    </Button>
    <Button
        variant="ghost"
        size="sm"
        disabled={!institution.is_active}
        onclick={() => onDelete?.(institution)}
        title="Delete"
        aria-label="Delete Institution"
    >
        <TrashIcon class="size-4" />
    </Button>
</div>
