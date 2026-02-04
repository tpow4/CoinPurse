<script lang="ts">
    import type { ImportPreviewSummary } from '$lib/types';
    import * as Card from '$lib/components/ui/card';
    import {
        TriangleAlert,
        Copy,
        FileText,
        CircleArrowUp,
    } from '@lucide/svelte';

    interface Props {
        summary: ImportPreviewSummary;
    }

    let { summary }: Props = $props();
    import * as m from '$lib/paraglide/messages';
</script>

<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
    <Card.Root class="py-4">
        <Card.Content class="flex items-center gap-3 px-4 py-0">
            <div
                class="bg-muted flex size-10 items-center justify-center rounded-full"
            >
                <FileText class="text-muted-foreground size-5" />
            </div>
            <div>
                <p class="text-muted-foreground text-sm">{m.imp_summary_total_rows()}</p>
                <p class="text-2xl font-bold">{summary.total_rows}</p>
            </div>
        </Card.Content>
    </Card.Root>

    <Card.Root class="py-4">
        <Card.Content class="flex items-center gap-3 px-4 py-0">
            <div
                class="flex size-10 items-center justify-center rounded-full bg-green-500/10"
            >
                <CircleArrowUp class="size-5 text-green-500" />
            </div>
            <div>
                <p class="text-muted-foreground text-sm">{m.imp_summary_new()}</p>
                <p class="text-2xl font-bold text-green-600">
                    {summary.valid_rows}
                </p>
            </div>
        </Card.Content>
    </Card.Root>

    <Card.Root class="py-4">
        <Card.Content class="flex items-center gap-3 px-4 py-0">
            <div
                class="flex size-10 items-center justify-center rounded-full bg-amber-500/10"
            >
                <Copy class="size-5 text-amber-500" />
            </div>
            <div>
                <p class="text-muted-foreground text-sm">{m.imp_summary_duplicates()}</p>
                <p class="text-2xl font-bold text-amber-600">
                    {summary.duplicate_count}
                </p>
            </div>
        </Card.Content>
    </Card.Root>

    <Card.Root class="py-4">
        <Card.Content class="flex items-center gap-3 px-4 py-0">
            <div
                class="flex size-10 items-center justify-center rounded-full bg-red-500/10"
            >
                <TriangleAlert class="size-5 text-red-500" />
            </div>
            <div>
                <p class="text-muted-foreground text-sm">{m.imp_summary_errors()}</p>
                <p class="text-2xl font-bold text-red-600">
                    {summary.validation_errors}
                </p>
            </div>
        </Card.Content>
    </Card.Root>
</div>
