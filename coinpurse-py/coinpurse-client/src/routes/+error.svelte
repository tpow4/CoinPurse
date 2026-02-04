<script lang="ts">
    import { page } from '$app/state';
    import { Button } from '$lib/components/ui/button';
    import * as m from '$lib/paraglide/messages';
</script>

<div class="flex min-h-screen items-center justify-center p-6">
    <div class="text-center max-w-md">
        <h1 class="text-6xl font-bold mb-4 text-primary">{page.status}</h1>
        <h2 class="text-2xl font-semibold mb-4">
            {#if page.status === 404}
                {m.error_page_not_found()}
            {:else}
                {m.error_title({ status: page.status })}
            {/if}
        </h2>
        <p class="text-muted-foreground mb-8">
            {page.error?.message || m.error_default_message()}
        </p>
        <div class="flex gap-4 justify-center">
            <Button href="/" variant="default">{m.error_go_home()}</Button>
            <Button onclick={() => window.history.back()} variant="outline">
                {m.error_go_back()}
            </Button>
        </div>
    </div>
</div>
