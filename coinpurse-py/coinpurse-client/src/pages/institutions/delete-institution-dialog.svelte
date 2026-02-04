<script lang="ts">
    import * as Dialog from '$lib/components/ui/dialog';
    import { Button } from '$lib/components/ui/button';
    import * as m from '$lib/paraglide/messages';

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
            <Dialog.Title>{m.inst_delete_title()}</Dialog.Title>
            <Dialog.Description>
                {m.inst_delete_confirm()}
            </Dialog.Description>
        </Dialog.Header>

        <p class="text-yellow-800 bg-yellow-50 p-2 rounded text-sm">
            {m.inst_delete_warning()}
        </p>

        <Dialog.Footer>
            <Button
                type="button"
                variant="outline"
                onclick={() => onOpenChange(false)}
            >
                {m.btn_cancel()}
            </Button>
            <Button
                variant="destructive"
                onclick={onConfirm}
                disabled={loading}
            >
                {loading ? m.btn_deleting() : m.btn_delete()}
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
