<script lang="ts">
	import ImportWizard from '../../pages/import/import-wizard.svelte';
	import * as m from '$lib/paraglide/messages';
</script>

<div class="mx-auto max-w-[1200px] p-8">
	<h1 class="mb-6 text-3xl font-bold">{m.imp_title()}</h1>
	<ImportWizard />
</div>
