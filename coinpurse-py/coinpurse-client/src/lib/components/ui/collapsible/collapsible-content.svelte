<script lang="ts">
	import { Collapsible as CollapsiblePrimitive } from 'bits-ui';
	import { cn } from '$lib/utils.js';

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: CollapsiblePrimitive.ContentProps & { class?: string } = $props();
</script>

<CollapsiblePrimitive.Content
	bind:ref
	class={cn('overflow-hidden transition-all', className)}
	{...restProps}
>
	{@render children?.()}
</CollapsiblePrimitive.Content>
