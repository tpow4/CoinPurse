<script lang="ts">
    import type { ImportConfirmResponse } from '$lib/types';
    import { ImportStatus } from '$lib/types';
    import { Button } from '$lib/components/ui/button';
    import * as Card from '$lib/components/ui/card';
    import { CircleCheck, CircleX, Upload, ArrowRight } from '@lucide/svelte';
    import * as m from '$lib/paraglide/messages';

    interface Props {
        confirmResponse: ImportConfirmResponse;
        onImportAnother: () => void;
    }

    let { confirmResponse, onImportAnother }: Props = $props();

    const isSuccess = $derived(
        confirmResponse.status === ImportStatus.COMPLETED
    );
</script>

<Card.Root class="mx-auto max-w-md">
    <Card.Header class="text-center">
        {#if isSuccess}
            <div
                class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-green-500/10"
            >
                <CircleCheck class="size-8 text-green-500" />
            </div>
            <Card.Title class="text-2xl">{m.imp_result_success_title()}</Card.Title>
            <Card.Description
                >{m.imp_result_success_desc()}</Card.Description
            >
        {:else}
            <div
                class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-red-500/10"
            >
                <CircleX class="size-8 text-red-500" />
            </div>
            <Card.Title class="text-2xl">{m.imp_result_fail_title()}</Card.Title>
            <Card.Description
                >{m.imp_result_fail_desc()}</Card.Description
            >
        {/if}
    </Card.Header>

    <Card.Content>
        <div class="space-y-3 rounded-lg border p-4">
            <div class="flex justify-between">
                <span class="text-muted-foreground">{m.imp_result_imported()}</span>
                <span class="font-medium text-green-600"
                    >{confirmResponse.imported_count}</span
                >
            </div>
            <div class="flex justify-between">
                <span class="text-muted-foreground">{m.imp_result_skipped()}</span>
                <span class="font-medium">{confirmResponse.skipped_count}</span>
            </div>
            {#if confirmResponse.duplicate_count > 0}
                <div class="flex justify-between">
                    <span class="text-muted-foreground"
                        >{m.imp_result_duplicates()}</span
                    >
                    <span class="font-medium text-amber-600"
                        >{confirmResponse.duplicate_count}</span
                    >
                </div>
            {/if}
        </div>
    </Card.Content>

    <Card.Footer class="flex flex-col gap-3">
        <Button
            type="button"
            variant="outline"
            onclick={onImportAnother}
            class="w-full"
        >
            <Upload class="mr-2 size-4" />
            {m.imp_result_import_another()}
        </Button>
        <Button href="/transactions" class="w-full">
            <span>{m.imp_result_view_transactions()}</span>
            <ArrowRight class="ml-2 size-4" />
        </Button>
    </Card.Footer>
</Card.Root>
