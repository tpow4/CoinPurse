<script lang="ts">
    import * as Dialog from '$lib/components/ui/dialog';
    import { Button } from '$lib/components/ui/button';

    interface Props {
        open: boolean;
        loading?: boolean;
        onOpenChange: (open: boolean) => void;
        onConfirm: () => void;
    }

    let {
        open = false,
        loading = false,
        onOpenChange,
        onConfirm,
    }: Props = $props();
</script>

<Dialog.Root {open} {onOpenChange}>
    <Dialog.Content class="sm:max-w-106.25">
        <Dialog.Header>
            <Dialog.Title>Delete Category</Dialog.Title>
            <Dialog.Description>
                Are you sure you want to delete this category?
            </Dialog.Description>
        </Dialog.Header>

        <p class="text-yellow-800 bg-yellow-50 p-2 rounded text-sm">
            This will perform a soft delete (set to inactive).
        </p>

        <Dialog.Footer>
            <Button
                type="button"
                variant="outline"
                onclick={() => onOpenChange(false)}
            >
                Cancel
            </Button>
            <Button
                variant="destructive"
                onclick={onConfirm}
                disabled={loading}
            >
                {loading ? 'Deleting...' : 'Delete'}
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
