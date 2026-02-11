<script lang="ts">
	import type { Account, Category, TransactionWithNames } from '$lib/types';
	import { transactionsApi } from '$lib/api/transactions';
	import { accountsApi } from '$lib/api/accounts';
	import { categoriesApi } from '$lib/api/categories';
	import TransactionsDataTable from '../../pages/transactions/transactions-data-table.svelte';
	import SelectedTransactionsSummary from '../../pages/transactions/selected-transactions-summary.svelte';
	import TransactionsBreakdownCharts, {
		type BreakdownDatum,
	} from '../../pages/transactions/transactions-breakdown-charts.svelte';
	import TransactionsCashFlowChart from '../../pages/transactions/transactions-cash-flow-chart.svelte';
	import TransactionsCashFlowRatioChart from '../../pages/transactions/transactions-cash-flow-ratio-chart.svelte';
	import TransactionsFilters, {
		type DatePreset,
		type TransactionFilter,
	} from '../../pages/transactions/transactions-filters.svelte';
	import { createColumns } from '../../pages/transactions/columns';
	import { Button } from '$lib/components/ui/button';
	import { Upload } from '@lucide/svelte';
	import * as m from '$lib/paraglide/messages';

	// Data state
	let transactions = $state<TransactionWithNames[]>([]);
	let filteredTransactions = $state<TransactionWithNames[]>([]);
	let accounts = $state<Account[]>([]);
	let categories = $state<Category[]>([]);
	let loading = $state(true);
	let error = $state('');

	// Filter state - backend filters
	let selectedAccountId = $state('');
	let selectedCategoryId = $state('');
	let datePreset = $state<DatePreset>('last30');
	let customStartDate = $state('');
	let customEndDate = $state('');
	let includeInactive = $state(false);

	// Filter state - client-side filters
	let searchTerm = $state('');
	let transactionFilter = $state<TransactionFilter>('all');
	let amountMin = $state(0);
	let amountMax = $state(0);

	// Dynamic amount range bounds
	let amountRangeMin = $state(0);
	let amountRangeMax = $state(0);
	let selectedTransactionIds = $state<Set<number>>(new Set());

	// Columns
	const columns = createColumns();
	const chartColors = [
		'var(--chart-1)',
		'var(--chart-2)',
		'var(--chart-3)',
		'var(--chart-4)',
		'var(--chart-5)',
	];

	const selectedTransactions = $derived(
		filteredTransactions.filter((tx) => selectedTransactionIds.has(tx.transaction_id))
	);

	const selectedTotalCents = $derived(
		selectedTransactions.reduce((sum, tx) => sum + tx.amount, 0)
	);
	const filteredTotalCents = $derived(
		filteredTransactions.reduce((sum, tx) => sum + tx.amount, 0)
	);
	const hasSelection = $derived(selectedTransactions.length > 0);

	function slugify(value: string): string {
		return value.toLowerCase().replaceAll(/[^a-z0-9]+/g, '-').replaceAll(/^-|-$/g, '');
	}

	function buildAmountBreakdown(
		items: TransactionWithNames[],
		getLabel: (tx: TransactionWithNames) => string,
		type: 'credits' | 'debits'
	): BreakdownDatum[] {
		const byLabel = new Map<string, number>();
		for (const tx of items) {
			if (type === 'credits' && tx.amount <= 0) continue;
			if (type === 'debits' && tx.amount >= 0) continue;
			const label = getLabel(tx);
			byLabel.set(label, (byLabel.get(label) ?? 0) + Math.abs(tx.amount));
		}

		return [...byLabel.entries()]
			.sort((a, b) => b[1] - a[1])
			.map(([label, cents], index) => ({
				key: `${slugify(label) || 'group'}-${index}`,
				label,
				value: cents / 100,
				color: chartColors[index % chartColors.length],
			}));
	}

	const breakdownType = $derived(transactionFilter === 'credits' ? 'credits' : 'debits');
	const showBreakdownCharts = $derived(transactionFilter !== 'all');

	const accountBreakdownData = $derived(
		buildAmountBreakdown(filteredTransactions, (tx) => tx.account_name, breakdownType)
	);
	const categoryBreakdownData = $derived(
		buildAmountBreakdown(filteredTransactions, (tx) => tx.category_name, breakdownType)
	);

	// Calculate date range from preset
	function getDateRange(preset: DatePreset): { start: string; end: string } {
		const today = new Date();
		const year = today.getFullYear();
		const month = today.getMonth();

		switch (preset) {
			case 'last30': {
				const start = new Date(today);
				start.setDate(start.getDate() - 30);
				return {
					start: start.toISOString().split('T')[0],
					end: today.toISOString().split('T')[0],
				};
			}
			case 'thisMonth': {
				const start = new Date(year, month, 1);
				return {
					start: start.toISOString().split('T')[0],
					end: today.toISOString().split('T')[0],
				};
			}
			case 'ytd': {
				const start = new Date(year, 0, 1);
				return {
					start: start.toISOString().split('T')[0],
					end: today.toISOString().split('T')[0],
				};
			}
			case 'thisYear': {
				const start = new Date(year, 0, 1);
				const end = new Date(year, 11, 31);
				return {
					start: start.toISOString().split('T')[0],
					end: end.toISOString().split('T')[0],
				};
			}
			case 'custom':
				return {
					start: customStartDate,
					end: customEndDate,
				};
		}
	}

	// Load reference data on mount
	async function loadReferenceData() {
		try {
			const [accountsRes, categoriesRes] = await Promise.all([
				accountsApi.getAll(false),
				categoriesApi.getAll(false),
			]);
			accounts = accountsRes;
			categories = categoriesRes;
		} catch (e) {
			console.error('Failed to load reference data:', e);
		}
	}

	// Load transactions from API
	async function loadTransactions() {
		loading = true;
		error = '';

		try {
			const dateRange = getDateRange(datePreset);
			const filters = {
				account_id: selectedAccountId ? Number(selectedAccountId) : undefined,
				category_id: selectedCategoryId ? Number(selectedCategoryId) : undefined,
				start_date: dateRange.start || undefined,
				end_date: dateRange.end || undefined,
				include_inactive: includeInactive,
			};

			transactions = await transactionsApi.getAllWithNames(filters);
			updateAmountRange();
			applyClientFilters();
		} catch (e) {
			error = e instanceof Error ? e.message : m.txn_error_load();
			console.error('Failed to load transactions:', e);
		} finally {
			loading = false;
		}
	}

	// Update amount range based on loaded data
	function updateAmountRange() {
		if (transactions.length === 0) {
			amountRangeMin = 0;
			amountRangeMax = 0;
			amountMin = 0;
			amountMax = 0;
			return;
		}

		const amounts = transactions.map((t) => t.amount);
		amountRangeMin = Math.min(...amounts);
		amountRangeMax = Math.max(...amounts);
		amountMin = amountRangeMin;
		amountMax = amountRangeMax;
	}

	// Apply client-side filters
	function applyClientFilters() {
		let result = transactions;

		// Search filter
		if (searchTerm) {
			const term = searchTerm.toLowerCase();
			result = result.filter((t) => t.description.toLowerCase().includes(term));
		}

		// Transaction type filter
		if (transactionFilter === 'credits') {
			result = result.filter((t) => t.amount > 0);
		} else if (transactionFilter === 'debits') {
			result = result.filter((t) => t.amount < 0);
		}

		// Amount range filter
		result = result.filter((t) => t.amount >= amountMin && t.amount <= amountMax);

		filteredTransactions = result;
	}

	// Clear all filters
	function clearFilters() {
		selectedAccountId = '';
		selectedCategoryId = '';
		datePreset = 'last30';
		customStartDate = '';
		customEndDate = '';
		includeInactive = false;
		searchTerm = '';
		transactionFilter = 'all';
		// Reset amount range to full range after reload
	}

	// Load on mount
	$effect(() => {
		loadReferenceData();
	});

	// Reload when backend filters change
	$effect(() => {
		// Track backend filter dependencies
		selectedAccountId;
		selectedCategoryId;
		datePreset;
		customStartDate;
		customEndDate;
		includeInactive;

		loadTransactions();
	});

	// Apply client filters when they change
	$effect(() => {
		// Track client filter dependencies
		searchTerm;
		transactionFilter;
		amountMin;
		amountMax;

		applyClientFilters();
	});
</script>

<div class="mx-auto max-w-350 p-8">
	<div class="mb-6 flex items-center justify-between">
		<h1 class="text-3xl font-bold">{m.txn_title()}</h1>
		<Button href="/import">
			<Upload class="mr-2 size-4" />
			{m.txn_btn_import()}
		</Button>
	</div>

	{#if error}
		<div class="mb-4 rounded bg-red-50 p-4 text-red-700">
			{error}
		</div>
	{/if}

	<div class="mb-6">
		<TransactionsFilters
			{searchTerm}
			{selectedAccountId}
			{selectedCategoryId}
			{datePreset}
			{customStartDate}
			{customEndDate}
			{transactionFilter}
			{amountMin}
			{amountMax}
			{amountRangeMin}
			{amountRangeMax}
			{includeInactive}
			{accounts}
			{categories}
			onSearchChange={(v) => (searchTerm = v)}
			onAccountChange={(v) => (selectedAccountId = v)}
			onCategoryChange={(v) => (selectedCategoryId = v)}
			onDatePresetChange={(v) => (datePreset = v)}
			onCustomStartDateChange={(v) => (customStartDate = v)}
			onCustomEndDateChange={(v) => (customEndDate = v)}
			onTransactionFilterChange={(v) => (transactionFilter = v)}
			onAmountMinChange={(v) => (amountMin = v)}
			onAmountMaxChange={(v) => (amountMax = v)}
			onIncludeInactiveChange={(v) => (includeInactive = v)}
			onClearFilters={clearFilters}
		/>
	</div>

	{#if loading}
		<div class="py-8 text-center text-gray-600">{m.txn_loading()}</div>
	{:else}
		<div class="mb-6">
			<SelectedTransactionsSummary
				selectedCount={selectedTransactions.length}
				filteredCount={filteredTransactions.length}
				totalCents={hasSelection ? selectedTotalCents : filteredTotalCents}
				showSelection={hasSelection}
			/>
		</div>

		<div class="mb-6">
			{#if showBreakdownCharts}
				<TransactionsBreakdownCharts
					accountData={accountBreakdownData}
					categoryData={categoryBreakdownData}
					type={breakdownType}
				/>
			{:else}
				<div class="grid gap-4 lg:grid-cols-2">
					<TransactionsCashFlowChart transactions={filteredTransactions} />
					<TransactionsCashFlowRatioChart transactions={filteredTransactions} />
				</div>
			{/if}
		</div>

		<TransactionsDataTable
			data={filteredTransactions}
			{columns}
			onSelectionChange={(ids) => (selectedTransactionIds = ids)}
		/>
	{/if}
</div>
