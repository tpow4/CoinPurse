<script lang="ts">
    import { page } from '$app/state';
    import { Button } from '$lib/components/ui/button';
</script>

<div class="flex min-h-screen items-center justify-center p-6">
    <div class="text-center max-w-md">
        <h1 class="text-6xl font-bold mb-4 text-primary">{page.status}</h1>
        <h2 class="text-2xl font-semibold mb-4">
            {#if page.status === 404}
                Page Not Found
            {:else}
                Error {page.status}
            {/if}
        </h2>
        <p class="text-muted-foreground mb-8">
            {page.error?.message || 'An unexpected error occurred'}
        </p>
        <div class="flex gap-4 justify-center">
            <Button href="/" variant="default">Go Home</Button>
            <Button onclick={() => window.history.back()} variant="outline">
                Go Back
            </Button>
        </div>
    </div>
</div>
