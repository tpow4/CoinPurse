<script lang="ts">
	import type { Account } from "$lib/types";
	import { Button } from "$lib/components/ui/button";

	interface Props {
		account: Account;
		onEdit?: (account: Account) => void;
		onDelete?: (account: Account) => void;
	}

	let { account, onEdit, onDelete }: Props = $props();
</script>

<div class="flex gap-2">
	<Button
		variant="secondary"
		size="sm"
		disabled={!account.active}
		onclick={() => onEdit?.(account)}
	>
		Edit
	</Button>
	<Button
		variant="destructive"
		size="sm"
		disabled={!account.active}
		onclick={() => onDelete?.(account)}
	>
		Delete
	</Button>
</div>
