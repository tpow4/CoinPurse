<script lang="ts">
    import type { Institution } from '$lib/types';
    import * as Dialog from '$lib/components/ui/dialog';
    import * as Field from '$lib/components/ui/field';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import * as m from '$lib/paraglide/messages';

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
        error = '',
        fieldErrors = {},
        onOpenChange,
        onSubmit,
    }: Props = $props();

    let formData = $state({ name: '' });

    // Update form data when editing institution changes
    $effect(() => {
        if (editingInstitution) {
            formData.name = editingInstitution.name;
        } else {
            formData.name = '';
        }
    });

    function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        if (loading) return;
        onSubmit({ name: formData.name });
    }
</script>

<Dialog.Root {open} {onOpenChange}>
    <Dialog.Content class="sm:max-w-106.25">
        <Dialog.Header>
            <Dialog.Title>
                {editingInstitution !== null
                    ? m.inst_dialog_title_edit()
                    : m.inst_dialog_title_add()}
            </Dialog.Title>
            <Dialog.Description>
                {editingInstitution !== null
                    ? m.inst_dialog_desc_edit()
                    : m.inst_dialog_desc_add()}
            </Dialog.Description>
        </Dialog.Header>

        <form onsubmit={handleSubmit}>
            <div class="space-y-4">
                {#if error}
                    <div class="bg-red-50 text-red-700 p-4 rounded mb-4">
                        {error}
                    </div>
                {/if}

                <Field.Field data-invalid={fieldErrors.name ? true : undefined}>
                    <Field.Label for="institution_name"
                        >{m.inst_field_name()}</Field.Label
                    >
                    <Input
                        type="text"
                        id="institution_name"
                        bind:value={formData.name}
                        placeholder={m.inst_field_name_placeholder()}
                        aria-invalid={fieldErrors.name ? true : undefined}
                    />
                    {#if fieldErrors.name}
                        <Field.Error>{fieldErrors.name}</Field.Error>
                    {/if}
                </Field.Field>
            </div>

            <Dialog.Footer class="mt-6">
                <Button
                    type="button"
                    variant="outline"
                    onclick={() => onOpenChange(false)}
                >
                    {m.btn_cancel()}
                </Button>
                <Button type="submit" disabled={loading}>
                    {loading
                        ? m.btn_saving()
                        : editingInstitution !== null
                          ? m.btn_update()
                          : m.btn_create()}
                </Button>
            </Dialog.Footer>
        </form>
    </Dialog.Content>
</Dialog.Root>
