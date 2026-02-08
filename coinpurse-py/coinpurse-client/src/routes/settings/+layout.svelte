<script lang="ts">
    import * as m from '$lib/paraglide/messages';

    let { children } = $props();
</script>

<div class="p-8 max-w-350 mx-auto">
    <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">{m.settings_title()}</h1>
        <p class="text-muted-foreground">{m.settings_description()}</p>
    </div>

    {@render children()}
</div>
