<script lang="ts">
	import type { Institution } from "$lib/types";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Field from "$lib/components/ui/field";
	import { Input } from "$lib/components/ui/input";
	import { Button } from "$lib/components/ui/button";

	interface Props {
		open: boolean;
		editingInstitution?: Institution | null;
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
		editingInstitution = null,
		loading = false,
		error = "",
		fieldErrors = {},
		onOpenChange,
		onSubmit,
	}: Props = $props();

	let formData = $state({ name: "" });

	// Update form data when editing institution changes
	$effect(() => {
		if (editingInstitution) {
			formData.name = editingInstitution.name;
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
				{editingInstitution !== null ? "Edit Institution" : "Add Institution"}
			</Dialog.Title>
			<Dialog.Description>
				{editingInstitution !== null
					? "Update the institution details below."
					: "Add a new financial institution to track your accounts."}
			</Dialog.Description>
		</Dialog.Header>

		<form onsubmit={handleSubmit}>
			<div class="space-y-4">
				{#if error}
					<div class="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>
				{/if}

				<Field.Field data-invalid={fieldErrors.name ? true : undefined}>
					<Field.Label for="institution_name">Institution Name</Field.Label>
					<Input
						type="text"
						id="institution_name"
						bind:value={formData.name}
						placeholder="e.g., Chase Bank"
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
					{loading ? "Saving..." : editingInstitution !== null ? "Update" : "Create"}
				</Button>
			</Dialog.Footer>
		</form>

    </Dialog.Content>
</Dialog.Root>
