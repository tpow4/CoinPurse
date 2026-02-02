<script lang="ts">
	import type { Category } from "$lib/types";
	import { Button } from "$lib/components/ui/button";

	interface Props {
		category: Category;
		onEdit?: (category: Category) => void;
		onDelete?: (category: Category) => void;
	}

	let { category, onEdit, onDelete }: Props = $props();
</script>

<div class="flex gap-2">
	<Button
		variant="secondary"
		size="sm"
		disabled={!category.is_active}
		onclick={() => onEdit?.(category)}
	>
		Edit
	</Button>
	<Button
		variant="destructive"
		size="sm"
		disabled={!category.is_active}
		onclick={() => onDelete?.(category)}
	>
		Delete
	</Button>
</div>
