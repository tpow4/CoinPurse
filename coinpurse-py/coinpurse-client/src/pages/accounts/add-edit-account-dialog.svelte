<script lang="ts">
	import type { Account, Institution, AccountType } from "$lib/types";
	import { AccountType as AccountTypeEnum } from "$lib/types";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Field from "$lib/components/ui/field";
	import { Combobox } from "$lib/components/ui/combobox";
	import { Input } from "$lib/components/ui/input";
	import { Button } from "$lib/components/ui/button";
	import { Checkbox } from "$lib/components/ui/checkbox";
	import { Label } from "$lib/components/ui/label";
    import { institutionsApi } from "$lib/api/institutions";

	interface Props {
		open: boolean;
		editingAccount?: Account | null;
		loading?: boolean;
		error?: string;
		fieldErrors?: {
			account_name?: string;
			institution_id?: string;
			account_type?: string;
			last_4_digits?: string;
		};
		onOpenChange: (open: boolean) => void;
		onSubmit: (data: {
			account_name: string;
			institution_id: number;
			account_type: AccountType;
			account_subtype: string | null;
			last_4_digits: string;
			tracks_transactions: boolean;
			tracks_balances: boolean;
			display_order: number;
		}) => void;
	}

	let {
		open = false,
		editingAccount = null,
		loading = false,
		error = "",
		fieldErrors = {},
		onOpenChange,
		onSubmit,
	}: Props = $props();

	type FormData = {
		account_name: string;
		institution_id: string;
		account_type: AccountType;
		account_subtype: string;
		last_4_digits: string;
		tracks_transactions: boolean;
		tracks_balances: boolean;
		display_order: number;
	};

	const defaultFormData: FormData = {
		account_name: "",
		institution_id: "",
		account_type: AccountTypeEnum.CHECKING,
		account_subtype: "",
		last_4_digits: "",
		tracks_transactions: true,
		tracks_balances: true,
		display_order: 0,
	};

	let institutions = $state<Institution[]>([]);
	let loadingInstitutions = $state(false);
	let institutionsLoaded = $state(false);

	let formData = $state<FormData>({ ...defaultFormData });

	// Account type options
	const accountTypes = [
		{ value: AccountTypeEnum.CHECKING, label: "Checking" },
		{ value: AccountTypeEnum.CREDIT_CARD, label: "Credit Card" },
		{ value: AccountTypeEnum.SAVINGS, label: "Savings" },
		{ value: AccountTypeEnum.INVESTMENT, label: "Investment" },
		{ value: AccountTypeEnum.RETIREMENT, label: "Retirement" },
		{ value: AccountTypeEnum.BROKERAGE, label: "Brokerage" },
	];

	// Lazy-load institutions when dialog opens
	$effect(() => {
		if (!open || institutionsLoaded || loadingInstitutions) return;

		loadingInstitutions = true;
		institutionsApi
			.getAll(false) // active only
			.then((res) => {
				institutions = res;
				institutionsLoaded = true;
			})
			.catch((e) => {
				console.error("Failed to load institutions:", e);
			})
			.finally(() => {
				loadingInstitutions = false;
			});
	});

	// Update form data when editing account changes
	$effect(() => {
		if (editingAccount) {
			Object.assign(formData, {
				account_name: editingAccount.account_name,
				institution_id: String(editingAccount.institution_id),
				account_type: editingAccount.account_type,
				account_subtype: editingAccount.account_subtype ?? "",
				last_4_digits: editingAccount.last_4_digits,
				tracks_transactions: editingAccount.tracks_transactions,
				tracks_balances: editingAccount.tracks_balances,
				display_order: editingAccount.display_order,
			} satisfies FormData);
			return;
		}

		Object.assign(formData, defaultFormData);
	});

	const institutionItems = $derived(
		institutions.map((institution) => ({
			value: String(institution.institution_id),
			label: institution.name,
		})),
	);

	function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		onSubmit({
			account_name: formData.account_name,
			institution_id: Number(formData.institution_id),
			account_type: formData.account_type,
			account_subtype: formData.account_subtype || null,
			last_4_digits: formData.last_4_digits,
			tracks_transactions: formData.tracks_transactions,
			tracks_balances: formData.tracks_balances,
			display_order: formData.display_order,
		});
	}
</script>

<Dialog.Root {open} {onOpenChange}>
	<Dialog.Content class="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title>
				{editingAccount !== null ? "Edit Account" : "Add Account"}
			</Dialog.Title>
			<Dialog.Description>
				{editingAccount !== null
					? "Update the account details below."
					: "Add a new account to track transactions and balances."}
			</Dialog.Description>
		</Dialog.Header>

		<form onsubmit={handleSubmit}>
			<div class="space-y-4">
				{#if error}
					<div class="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>
				{/if}

				<!-- Account Name -->
				<Field.Field data-invalid={fieldErrors.account_name ? true : undefined}>
					<Field.Label for="account_name">Account Name</Field.Label>
					<Input
						type="text"
						id="account_name"
						bind:value={formData.account_name}
						placeholder="e.g., Primary Checking"
						aria-invalid={fieldErrors.account_name ? true : undefined}
					/>
					{#if fieldErrors.account_name}
						<Field.Error>{fieldErrors.account_name}</Field.Error>
					{/if}
				</Field.Field>

				<!-- Institution -->
				<Field.Field data-invalid={fieldErrors.institution_id ? true : undefined}>
					<Field.Label for="institution_id">Institution</Field.Label>
                    <Combobox
						id="institution"
						items={institutionItems}
						bind:value={formData.institution_id}
						placeholder="Select institution"
						searchPlaceholder="Search institutions..."
						ariaInvalid={fieldErrors.institution_id ? true : false}
					/>
					{#if fieldErrors.institution_id}
						<Field.Error>{fieldErrors.institution_id}</Field.Error>
					{/if}
				</Field.Field>

				<!-- Account Type -->
				<Field.Field data-invalid={fieldErrors.account_type ? true : undefined}>
					<Field.Label for="account_type">Account Type</Field.Label>
					<Combobox
						id="account_type"
						items={accountTypes}
						bind:value={formData.account_type}
						placeholder="Select account type"
						searchPlaceholder="Search account types..."
						ariaInvalid={fieldErrors.account_type ? true : false}
					/>
					{#if fieldErrors.account_type}
						<Field.Error>{fieldErrors.account_type}</Field.Error>
					{/if}
				</Field.Field>

				<!-- Account Subtype -->
				<Field.Field>
					<Field.Label for="account_subtype">Account Subtype (Optional)</Field.Label>
					<Input
						type="text"
						id="account_subtype"
						bind:value={formData.account_subtype}
						placeholder="e.g., Student Checking"
					/>
				</Field.Field>

				<!-- Last 4 Digits -->
				<Field.Field data-invalid={fieldErrors.last_4_digits ? true : undefined}>
					<Field.Label for="last_4_digits">Last 4 Digits</Field.Label>
					<Input
						type="text"
						id="last_4_digits"
						bind:value={formData.last_4_digits}
						placeholder="1234"
						maxlength={4}
						aria-invalid={fieldErrors.last_4_digits ? true : undefined}
					/>
					{#if fieldErrors.last_4_digits}
						<Field.Error>{fieldErrors.last_4_digits}</Field.Error>
					{/if}
				</Field.Field>

				<!-- Display Order -->
				<Field.Field>
					<Field.Label for="display_order">Display Order</Field.Label>
					<Input
						type="number"
						id="display_order"
						bind:value={formData.display_order}
						placeholder="0"
					/>
				</Field.Field>

				<!-- Tracks Transactions -->
				<div class="flex items-center gap-2">
					<Checkbox
						id="tracks_transactions"
						checked={formData.tracks_transactions}
						onCheckedChange={(checked) => {
							formData.tracks_transactions = checked === true;
						}}
					/>
					<Label
						for="tracks_transactions"
						class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
					>
						Track Transactions
					</Label>
				</div>

				<!-- Tracks Balances -->
				<div class="flex items-center gap-2">
					<Checkbox
						id="tracks_balances"
						checked={formData.tracks_balances}
						onCheckedChange={(checked) => {
							formData.tracks_balances = checked === true;
						}}
					/>
					<Label
						for="tracks_balances"
						class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
					>
						Track Balances
					</Label>
				</div>
			</div>

			<Dialog.Footer class="mt-6">
				<Button type="button" variant="outline" onclick={() => onOpenChange(false)}>
					Cancel
				</Button>
				<Button type="submit" disabled={loading}>
					{loading ? "Saving..." : editingAccount !== null ? "Update" : "Create"}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
