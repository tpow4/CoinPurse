<script lang="ts">
    import type { Institution } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import PencilIcon from '@lucide/svelte/icons/pencil';
    import TrashIcon from '@lucide/svelte/icons/trash-2';
    import * as m from '$lib/paraglide/messages';

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
        title={m.inst_action_edit()}
        aria-label={m.inst_action_edit_label()}
    >
        <PencilIcon class="size-4" />
    </Button>
    <Button
        variant="ghost"
        size="sm"
        disabled={!institution.is_active}
        onclick={() => onDelete?.(institution)}
        title={m.inst_action_delete()}
        aria-label={m.inst_action_delete_label()}
    >
        <TrashIcon class="size-4" />
    </Button>
</div>
