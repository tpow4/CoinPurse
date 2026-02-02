<script lang="ts">
	import type { Category } from "$lib/types";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Field from "$lib/components/ui/field";
	import { Input } from "$lib/components/ui/input";
	import { Button } from "$lib/components/ui/button";

	interface Props {
		open: boolean;
		editingCategory?: Category | null;
		loading?: boolean;
		error?: string;
		fieldErrors?: {
			name?: string;
		};
		onOpenChange: (open: boolean) => void;
		onSubmit: (data: { name: string }) => void;
	}

	let {
		open = false,
		editingCategory = null,
		loading = false,
		error = "",
		fieldErrors = {},
		onOpenChange,
		onSubmit,
	}: Props = $props();

	let formData = $state({ name: "" });

	// Update form data when editing category changes
	$effect(() => {
		if (editingCategory) {
			formData.name = editingCategory.name;
		} else {
			formData.name = "";
		}
	});

	function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		onSubmit({ name: formData.name });
	}
</script>

<Dialog.Root {open} {onOpenChange}>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>
				{editingCategory !== null ? "Edit Category" : "Add Category"}
			</Dialog.Title>
			<Dialog.Description>
				{editingCategory !== null
					? "Update the category details below."
					: "Add a new category to organize your transactions."}
			</Dialog.Description>
		</Dialog.Header>

		<form onsubmit={handleSubmit}>
			<div class="space-y-4">
				{#if error}
					<div class="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>
				{/if}

				<Field.Field data-invalid={fieldErrors.name ? true : undefined}>
					<Field.Label for="category_name">Category Name</Field.Label>
					<Input
						type="text"
						id="category_name"
						bind:value={formData.name}
						placeholder="e.g., Groceries"
						aria-invalid={fieldErrors.name ? true : undefined}
					/>
					{#if fieldErrors.name}
						<Field.Error>{fieldErrors.name}</Field.Error>
					{/if}
				</Field.Field>
			</div>

			<Dialog.Footer class="mt-6">
				<Button type="button" variant="outline" onclick={() => onOpenChange(false)}>
					Cancel
				</Button>
				<Button type="submit" disabled={loading}>
					{loading ? "Saving..." : editingCategory !== null ? "Update" : "Create"}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
