<script lang="ts">
    import { Input } from '$lib/components/ui/input';
    import { formatCurrency, getCurrencySymbol } from '$lib/format';

    interface Props {
        min: number;
        max: number;
        minValue: number;
        maxValue: number;
        onMinChange: (value: number) => void;
        onMaxChange: (value: number) => void;
    }

    let { min, max, minValue, maxValue, onMinChange, onMaxChange }: Props =
        $props();

    // Convert dollars input to cents
    function handleMinInput(e: Event) {
        const value = (e.target as HTMLInputElement).value;
        const dollars = parseFloat(value) || 0;
        onMinChange(Math.round(dollars * 100));
    }

    function handleMaxInput(e: Event) {
        const value = (e.target as HTMLInputElement).value;
        const dollars = parseFloat(value) || 0;
        onMaxChange(Math.round(dollars * 100));
    }

    const minDollars = $derived((minValue / 100).toFixed(0));
    const maxDollars = $derived((maxValue / 100).toFixed(0));
    const rangeDollarsMin = $derived((min / 100).toFixed(0));
    const rangeDollarsMax = $derived((max / 100).toFixed(0));
    const symbol = $derived(getCurrencySymbol());
</script>

<div class="flex items-center gap-2">
    <div class="flex items-center gap-1">
        <span class="text-sm text-gray-500">{symbol}</span>
        <Input
            type="number"
            class="w-24"
            value={minDollars}
            min={rangeDollarsMin}
            max={rangeDollarsMax}
            onchange={handleMinInput}
        />
    </div>
    <span class="text-gray-400">–</span>
    <div class="flex items-center gap-1">
        <span class="text-sm text-gray-500">{symbol}</span>
        <Input
            type="number"
            class="w-24"
            value={maxDollars}
            min={rangeDollarsMin}
            max={rangeDollarsMax}
            onchange={handleMaxInput}
        />
    </div>
    <span class="text-xs text-gray-400">
        ({formatCurrency(min / 100)} – {formatCurrency(max / 100)})
    </span>
</div>
