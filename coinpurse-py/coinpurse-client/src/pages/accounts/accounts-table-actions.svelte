<script lang="ts">
    import type { Account } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import PencilIcon from '@lucide/svelte/icons/pencil';
    import TrashIcon from '@lucide/svelte/icons/trash-2';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        account: Account;
        onEdit?: (account: Account) => void;
        onDelete?: (account: Account) => void;
    }

    let { account, onEdit, onDelete }: Props = $props();
</script>

<div class="flex gap-1 justify-end">
    <Button
        variant="ghost"
        size="sm"
        disabled={!account.active}
        onclick={() => onEdit?.(account)}
        title={m.acct_action_edit()}
        aria-label={m.acct_action_edit()}
    >
        <PencilIcon class="size-4" />
    </Button>
    <Button
        variant="ghost"
        size="sm"
        disabled={!account.active}
        onclick={() => onDelete?.(account)}
        title={m.acct_action_delete()}
        aria-label={m.acct_action_delete()}
    >
        <TrashIcon class="size-4" />
    </Button>
</div>
