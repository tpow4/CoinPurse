<script lang="ts">
	import type { Institution } from "$lib/types";
	import { Button } from "$lib/components/ui/button";

	interface Props {
		institution: Institution;
		onEdit?: (institution: Institution) => void;
		onDelete?: (institution: Institution) => void;
	}

	let { institution, onEdit, onDelete }: Props = $props();
</script>

<div class="flex gap-2">
	<Button
		variant="secondary"
		size="sm"
		disabled={!institution.is_active}
		onclick={() => onEdit?.(institution)}
	>
		Edit
	</Button>
	<Button
		variant="destructive"
		size="sm"
		disabled={!institution.is_active}
		onclick={() => onDelete?.(institution)}
	>
		Delete
	</Button>
</div>
