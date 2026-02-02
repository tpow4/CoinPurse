<script lang="ts">
	import type { Category } from "$lib/types";
	import { Button } from "$lib/components/ui/button";
	import PencilIcon from "@lucide/svelte/icons/pencil";
	import TrashIcon from "@lucide/svelte/icons/trash-2";

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
		title="Edit"
	>
		<PencilIcon class="size-4" />
	</Button>
	<Button
		variant="ghost"
		size="sm"
		disabled={!category.is_active}
		onclick={() => onDelete?.(category)}
		title="Delete"
	>
		<TrashIcon class="size-4" />
	</Button>
</div>
