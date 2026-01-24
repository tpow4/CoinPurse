<script lang="ts">
	import type { Account, Category } from '$lib/types';
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Label } from '$lib/components/ui/label';
	import { Combobox } from '$lib/components/ui/combobox';
	import * as Select from '$lib/components/ui/select';
	import AmountRangeSlider from './amount-range-slider.svelte';

	export type DatePreset = 'last30' | 'thisMonth' | 'ytd' | 'thisYear' | 'custom';
	export type TransactionFilter = 'all' | 'credits' | 'debits';

	interface Props {
		// Filter values
		searchTerm: string;
		selectedAccountId: string;
		selectedCategoryId: string;
		datePreset: DatePreset;
		customStartDate: string;
		customEndDate: string;
		transactionFilter: TransactionFilter;
		amountMin: number;
		amountMax: number;
		amountRangeMin: number;
		amountRangeMax: number;
		includeInactive: boolean;

		// Data for dropdowns
		accounts: Account[];
		categories: Category[];

		// Event handlers
		onSearchChange: (value: string) => void;
		onAccountChange: (value: string) => void;
		onCategoryChange: (value: string) => void;
		onDatePresetChange: (value: DatePreset) => void;
		onCustomStartDateChange: (value: string) => void;
		onCustomEndDateChange: (value: string) => void;
		onTransactionFilterChange: (value: TransactionFilter) => void;
		onAmountMinChange: (value: number) => void;
		onAmountMaxChange: (value: number) => void;
		onIncludeInactiveChange: (value: boolean) => void;
		onClearFilters: () => void;
	}

	let {
		searchTerm,
		selectedAccountId,
		selectedCategoryId,
		datePreset,
		customStartDate,
		customEndDate,
		transactionFilter,
		amountMin,
		amountMax,
		amountRangeMin,
		amountRangeMax,
		includeInactive,
		accounts,
		categories,
		onSearchChange,
		onAccountChange,
		onCategoryChange,
		onDatePresetChange,
		onCustomStartDateChange,
		onCustomEndDateChange,
		onTransactionFilterChange,
		onAmountMinChange,
		onAmountMaxChange,
		onIncludeInactiveChange,
		onClearFilters,
	}: Props = $props();

	// Local state for bound values
	let localAccountId = $state(selectedAccountId);
	let localCategoryId = $state(selectedCategoryId);
	let localDatePreset = $state(datePreset);

	// Sync local state with props
	$effect(() => {
		localAccountId = selectedAccountId;
	});
	$effect(() => {
		localCategoryId = selectedCategoryId;
	});
	$effect(() => {
		localDatePreset = datePreset;
	});

	// Notify parent when local values change
	$effect(() => {
		if (localAccountId !== selectedAccountId) {
			onAccountChange(localAccountId);
		}
	});
	$effect(() => {
		if (localCategoryId !== selectedCategoryId) {
			onCategoryChange(localCategoryId);
		}
	});
	$effect(() => {
		if (localDatePreset !== datePreset) {
			onDatePresetChange(localDatePreset as DatePreset);
		}
	});

	function getDatePresetLabel(preset: DatePreset): string {
		switch (preset) {
			case 'last30':
				return 'Last 30 Days';
			case 'thisMonth':
				return 'This Month';
			case 'ytd':
				return 'Year to Date';
			case 'thisYear':
				return 'This Year';
			case 'custom':
				return 'Custom';
		}
	}

	const datePresetLabel = $derived(getDatePresetLabel(localDatePreset as DatePreset));

	const accountItems = $derived([
		{ value: '', label: 'All Accounts' },
		...accounts.map((a) => ({
			value: String(a.account_id),
			label: a.account_name,
		})),
	]);

	const categoryItems = $derived([
		{ value: '', label: 'All Categories' },
		...categories.map((c) => ({
			value: String(c.category_id),
			label: c.name,
		})),
	]);

	const datePresets: { value: DatePreset; label: string }[] = [
		{ value: 'last30', label: 'Last 30 Days' },
		{ value: 'thisMonth', label: 'This Month' },
		{ value: 'ytd', label: 'Year to Date' },
		{ value: 'thisYear', label: 'This Year' },
		{ value: 'custom', label: 'Custom' },
	];

	let debounceTimer: ReturnType<typeof setTimeout>;
	function handleSearchInput(e: Event) {
		const value = (e.target as HTMLInputElement).value;
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => {
			onSearchChange(value);
		}, 300);
	}
</script>

<div class="space-y-4 rounded-lg border p-4">
	<!-- Row 1: Search, Account, Category -->
	<div class="flex flex-wrap gap-4">
		<div class="min-w-[200px] flex-1">
			<Label for="search" class="mb-1 block text-sm">Search</Label>
			<Input
				type="text"
				id="search"
				placeholder="Search description..."
				value={searchTerm}
				oninput={handleSearchInput}
			/>
		</div>

		<div class="min-w-[180px]">
			<Label for="account" class="mb-1 block text-sm">Account</Label>
			<Combobox
				id="account"
				items={accountItems}
				bind:value={localAccountId}
				placeholder="All Accounts"
				searchPlaceholder="Search accounts..."
			/>
		</div>

		<div class="min-w-[180px]">
			<Label for="category" class="mb-1 block text-sm">Category</Label>
			<Combobox
				id="category"
				items={categoryItems}
				bind:value={localCategoryId}
				placeholder="All Categories"
				searchPlaceholder="Search categories..."
			/>
		</div>
	</div>

	<!-- Row 2: Date Range -->
	<div class="flex flex-wrap items-end gap-4">
		<div class="min-w-[160px]">
			<Label for="date-preset" class="mb-1 block text-sm">Date Range</Label>
			<Select.Root type="single" bind:value={localDatePreset}>
				<Select.Trigger id="date-preset" class="w-full">
					{datePresetLabel}
				</Select.Trigger>
				<Select.Content>
					{#each datePresets as preset}
						<Select.Item value={preset.value} label={preset.label} />
					{/each}
				</Select.Content>
			</Select.Root>
		</div>

		{#if datePreset === 'custom'}
			<div class="min-w-[140px]">
				<Label for="start-date" class="mb-1 block text-sm">Start Date</Label>
				<Input
					type="date"
					id="start-date"
					value={customStartDate}
					onchange={(e) => onCustomStartDateChange((e.target as HTMLInputElement).value)}
				/>
			</div>

			<div class="min-w-[140px]">
				<Label for="end-date" class="mb-1 block text-sm">End Date</Label>
				<Input
					type="date"
					id="end-date"
					value={customEndDate}
					onchange={(e) => onCustomEndDateChange((e.target as HTMLInputElement).value)}
				/>
			</div>
		{/if}
	</div>

	<!-- Row 3: Transaction Type Toggle, Amount Range -->
	<div class="flex flex-wrap items-end gap-6">
		<!-- Credit/Debit Toggle -->
		<div>
			<Label class="mb-1 block text-sm">Type</Label>
			<div class="flex rounded-md border">
				<Button
					type="button"
					variant={transactionFilter === 'all' ? 'default' : 'ghost'}
					size="sm"
					class="rounded-r-none"
					onclick={() => onTransactionFilterChange('all')}
				>
					All
				</Button>
				<Button
					type="button"
					variant={transactionFilter === 'credits' ? 'default' : 'ghost'}
					size="sm"
					class="rounded-none border-x"
					onclick={() => onTransactionFilterChange('credits')}
				>
					Credits
				</Button>
				<Button
					type="button"
					variant={transactionFilter === 'debits' ? 'default' : 'ghost'}
					size="sm"
					class="rounded-l-none"
					onclick={() => onTransactionFilterChange('debits')}
				>
					Debits
				</Button>
			</div>
		</div>

		<!-- Amount Range -->
		<div class="min-w-[250px] flex-1 max-w-[400px]">
			<Label class="mb-1 block text-sm">Amount Range</Label>
			<AmountRangeSlider
				min={amountRangeMin}
				max={amountRangeMax}
				minValue={amountMin}
				maxValue={amountMax}
				onMinChange={onAmountMinChange}
				onMaxChange={onAmountMaxChange}
			/>
		</div>
	</div>

	<!-- Row 4: Include Inactive, Clear Filters -->
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<Checkbox
				id="include-inactive"
				checked={includeInactive}
				onCheckedChange={(checked) => onIncludeInactiveChange(checked === true)}
			/>
			<Label
				for="include-inactive"
				class="cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
			>
				Include inactive
			</Label>
		</div>

		<Button type="button" variant="outline" size="sm" onclick={onClearFilters}>
			Clear Filters
		</Button>
	</div>
</div>
