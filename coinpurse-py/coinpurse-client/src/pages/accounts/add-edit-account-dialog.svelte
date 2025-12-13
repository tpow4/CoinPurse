<script lang="ts">
	import { onMount } from "svelte";
	import type { Account, Institution, AccountType } from "$lib/types";
	import { AccountType as AccountTypeEnum } from "$lib/types";
	import { api, ApiException } from "$lib/api";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Field from "$lib/components/ui/field";
	import * as Select from "$lib/components/ui/select";
	import { Input } from "$lib/components/ui/input";
	import { Button } from "$lib/components/ui/button";
	import { Checkbox } from "$lib/components/ui/checkbox";
	import { Label } from "$lib/components/ui/label";

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

	export let open: boolean = false;
	export let editingAccount: Account | null = null;
	export let loading: boolean = false;
	export let error: string = "";
	export let fieldErrors: {
		account_name?: string;
		institution_id?: string;
		account_type?: string;
		last_4_digits?: string;
	} = {};
	export let onOpenChange: (open: boolean) => void;
	export let onSubmit: (data: {
		account_name: string;
		institution_id: number;
		account_type: AccountType;
		account_subtype: string | null;
		last_4_digits: string;
		tracks_transactions: boolean;
		tracks_balances: boolean;
		display_order: number;
	}) => void;

	let institutions: Institution[] = [];
	let loadingInstitutions = false;

	let formData = {
		account_name: "",
		institution_id: "" as string,
		account_type: AccountTypeEnum.CHECKING as AccountType,
		account_subtype: "",
		last_4_digits: "",
		tracks_transactions: true,
		tracks_balances: true,
		display_order: 0,
	};

	// Account type options
	const accountTypes = [
		{ value: AccountTypeEnum.CHECKING, label: "Checking" },
		{ value: AccountTypeEnum.CREDIT_CARD, label: "Credit Card" },
		{ value: AccountTypeEnum.SAVINGS, label: "Savings" },
		{ value: AccountTypeEnum.INVESTMENT, label: "Investment" },
		{ value: AccountTypeEnum.RETIREMENT, label: "Retirement" },
		{ value: AccountTypeEnum.BROKERAGE, label: "Brokerage" },
	];

	// Load institutions on mount
	onMount(async () => {
		loadingInstitutions = true;
		try {
			institutions = await api.institutions.getAll(false); // active only
		} catch (e) {
			console.error("Failed to load institutions:", e);
		} finally {
			loadingInstitutions = false;
		}
	});

	// Update form data when editing account changes
	$: if (editingAccount) {
		formData.account_name = editingAccount.account_name;
		formData.institution_id = String(editingAccount.institution_id);
		formData.account_type = editingAccount.account_type;
		formData.account_subtype = editingAccount.account_subtype || "";
		formData.last_4_digits = editingAccount.last_4_digits;
		formData.tracks_transactions = editingAccount.tracks_transactions;
		formData.tracks_balances = editingAccount.tracks_balances;
		formData.display_order = editingAccount.display_order;
	} else {
		formData.account_name = "";
		formData.institution_id = "";
		formData.account_type = AccountTypeEnum.CHECKING;
		formData.account_subtype = "";
		formData.last_4_digits = "";
		formData.tracks_transactions = true;
		formData.tracks_balances = true;
		formData.display_order = 0;
	}

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
					<Select.Root
						type="multiple"
						value={formData.institution_id ? [formData.institution_id] : []}
						onValueChange={(v: string[]) => formData.institution_id = v[0] || ""}
						disabled={loadingInstitutions}
					>
						<Select.Trigger class="w-full">
							<span data-slot="select-value">
								{institutions.find(i => i.institution_id.toString() === formData.institution_id)?.name || "Select an institution"}
							</span>
						</Select.Trigger>
						<Select.Content>
							{#each institutions as institution}
								<Select.Item value={institution.institution_id.toString()} label={institution.name}>
									{institution.name}
								</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
					{#if fieldErrors.institution_id}
						<Field.Error>{fieldErrors.institution_id}</Field.Error>
					{/if}
				</Field.Field>

				<!-- Account Type -->
				<Field.Field data-invalid={fieldErrors.account_type ? true : undefined}>
					<Field.Label for="account_type">Account Type</Field.Label>
					<Select.Root
						type="multiple"
						value={formData.account_type ? [formData.account_type] : []}
						onValueChange={(v: string[]) => formData.account_type = (v[0] as AccountType) || AccountTypeEnum.CHECKING}
					>
						<Select.Trigger class="w-full">
							<span data-slot="select-value">
								{accountTypes.find(t => t.value === formData.account_type)?.label || "Select account type"}
							</span>
						</Select.Trigger>
						<Select.Content>
							{#each accountTypes as type}
								<Select.Item value={type.value} label={type.label}>
									{type.label}
								</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
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
