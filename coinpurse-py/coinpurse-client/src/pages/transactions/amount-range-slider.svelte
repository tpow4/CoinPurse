<script lang="ts">
	import { Slider } from '$lib/components/ui/slider';
	import { formatCurrency } from '$lib/format';

	interface Props {
		min: number;
		max: number;
		minValue: number;
		maxValue: number;
		onMinChange: (value: number) => void;
		onMaxChange: (value: number) => void;
	}

	let { min, max, minValue, maxValue, onMinChange, onMaxChange }: Props = $props();

	const minDollars = $derived(Math.round(min / 100));
	const maxDollars = $derived(Math.round(max / 100));
	const sliderValues = $derived([Math.round(minValue / 100), Math.round(maxValue / 100)]);
	const isDisabled = $derived(minDollars === maxDollars);

	function handleValueChange(values: number[]) {
		onMinChange(Math.round(values[0] * 100));
		onMaxChange(Math.round(values[1] * 100));
	}
</script>

<div class="flex min-w-0 flex-1 flex-col gap-1.5">
	<div class="text-muted-foreground flex justify-between text-xs">
		<span>{formatCurrency(minValue / 100)}</span>
		<span>{formatCurrency(maxValue / 100)}</span>
	</div>
	<Slider
		min={minDollars}
		max={maxDollars}
		step={1}
		value={sliderValues}
		disabled={isDisabled}
		onValueChange={handleValueChange}
	/>
</div>
