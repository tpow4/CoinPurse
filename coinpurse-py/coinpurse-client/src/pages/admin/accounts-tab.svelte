<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiException } from "../../lib/api";
  import type {
    Account,
    AccountCreate,
    AccountUpdate,
    AccountType,
    Institution,
  } from "../../lib/types";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import { Label } from "$lib/components/ui/label";
  import { Checkbox } from "$lib/components/ui/checkbox";
  import AccountsDataTable from "../accounts/accounts-data-table.svelte";
  import DeleteAccountDialog from "../accounts/delete-account-dialog.svelte";
  import AddEditAccountDialog from "../accounts/add-edit-account-dialog.svelte";
  import { createColumns, type AccountWithInstitution } from "../accounts/columns";

  // State
  let accounts: Account[] = [];
  let institutions: Institution[] = [];
  let accountsWithInstitutions: AccountWithInstitution[] = [];
  let loading = false;
  let error = "";
  let searchTerm = "";
  let includeInactive = false;

  // Add/edit state
  let showForm = false;
  let editingAccount: Account | null = null;
  let formErrors = {
    account_name: "",
    institution_id: "",
    account_type: "",
    last_4_digits: "",
  };
  let formError = "";
  let formLoading = false;

  // Delete state
  let deleteConfirm: number | null = null;
  let deleteLoading = false;

  // Load accounts and institutions on mount
  onMount(() => {
    loadData();
  });

  // Create grid columns with callbacks
  const columns = createColumns({
    onEdit: openEditForm,
    onDelete: (account) => (deleteConfirm = account.account_id),
  });

  async function loadData() {
    loading = true;
    error = "";
    try {
      // Load both accounts and institutions in parallel
      const [accountsData, institutionsData] = await Promise.all([
        api.accounts.getAll(includeInactive),
        api.institutions.getAll(false), // active only for lookup
      ]);

      accounts = accountsData;
      institutions = institutionsData;

      // Join accounts with institution names
      accountsWithInstitutions = joinAccountsWithInstitutions(accounts, institutions);
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = "Failed to load accounts";
      }
    } finally {
      loading = false;
    }
  }

  function joinAccountsWithInstitutions(
    accounts: Account[],
    institutions: Institution[]
  ): AccountWithInstitution[] {
    // Create institution lookup map
    const institutionMap = institutions.reduce((map, inst) => {
      map[inst.institution_id] = inst.name;
      return map;
    }, {} as Record<number, string>);

    // Join accounts with institution names
    return accounts.map((account) => ({
      ...account,
      institution_name: institutionMap[account.institution_id] || "Unknown",
    }));
  }

  async function handleSearch() {
    if (!searchTerm.trim()) {
      loadData();
      return;
    }

    loading = true;
    error = "";
    try {
      accounts = await api.accounts.search(searchTerm);
      accountsWithInstitutions = joinAccountsWithInstitutions(accounts, institutions);
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = "Search failed";
      }
    } finally {
      loading = false;
    }
  }

  function validateForm(data: {
    account_name: string;
    institution_id: number;
    account_type: AccountType;
    last_4_digits: string;
  }): boolean {
    formErrors = {
      account_name: "",
      institution_id: "",
      account_type: "",
      last_4_digits: "",
    };

    let isValid = true;

    if (!data.account_name.trim()) {
      formErrors.account_name = "Account name is required";
      isValid = false;
    } else if (data.account_name.length > 100) {
      formErrors.account_name = "Name is too long (max 100 characters)";
      isValid = false;
    }

    if (!data.institution_id || data.institution_id === 0) {
      formErrors.institution_id = "Institution is required";
      isValid = false;
    }

    if (!data.account_type) {
      formErrors.account_type = "Account type is required";
      isValid = false;
    }

    if (data.last_4_digits && data.last_4_digits.length > 4) {
      formErrors.last_4_digits = "Last 4 digits must be 4 characters or less";
      isValid = false;
    }

    return isValid;
  }

  function openCreateForm() {
    editingAccount = null;
    formErrors = {
      account_name: "",
      institution_id: "",
      account_type: "",
      last_4_digits: "",
    };
    formError = "";
    showForm = true;
  }

  function openEditForm(account: Account) {
    editingAccount = account;
    formErrors = {
      account_name: "",
      institution_id: "",
      account_type: "",
      last_4_digits: "",
    };
    formError = "";
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingAccount = null;
    formErrors = {
      account_name: "",
      institution_id: "",
      account_type: "",
      last_4_digits: "",
    };
    formError = "";
  }

  async function handleFormSubmit(data: {
    account_name: string;
    institution_id: number;
    account_type: AccountType;
    account_subtype: string | null;
    last_4_digits: string;
    tracks_transactions: boolean;
    tracks_balances: boolean;
    display_order: number;
  }) {
    formError = "";

    if (!validateForm(data)) {
      return;
    }

    formLoading = true;
    try {
      if (editingAccount !== null) {
        // Update existing
        const updateData: AccountUpdate = {
          account_name: data.account_name,
          institution_id: data.institution_id,
          account_type: data.account_type,
          account_subtype: data.account_subtype,
          last_4_digits: data.last_4_digits,
          tracks_transactions: data.tracks_transactions,
          tracks_balances: data.tracks_balances,
          display_order: data.display_order,
        };
        await api.accounts.update(editingAccount.account_id, updateData);
      } else {
        // Create new
        const createData: AccountCreate = {
          account_name: data.account_name,
          institution_id: data.institution_id,
          account_type: data.account_type,
          account_subtype: data.account_subtype,
          last_4_digits: data.last_4_digits,
          tracks_transactions: data.tracks_transactions,
          tracks_balances: data.tracks_balances,
          display_order: data.display_order,
        };
        await api.accounts.create(createData);
      }

      closeForm();
      loadData();
    } catch (e) {
      if (e instanceof ApiException) {
        formError = e.detail;
      } else {
        formError = "Failed to save account";
      }
    } finally {
      formLoading = false;
    }
  }

  async function handleDelete(id: number, hardDelete = false) {
    deleteLoading = true;
    error = "";
    try {
      await api.accounts.delete(id, hardDelete);
      deleteConfirm = null;
      loadData();
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = "Failed to delete account";
      }
    } finally {
      deleteLoading = false;
    }
  }
</script>

<div>
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold">Accounts</h2>
    <Button onclick={openCreateForm}>+ Add Account</Button>
  </div>

  <!-- Search and filters -->
  <div class="flex gap-4 mb-6 items-center">
    <div class="flex-1 max-w-[400px]">
      <Input
        type="text"
        placeholder="Search accounts..."
        bind:value={searchTerm}
        oninput={handleSearch}
      />
    </div>
    <div class="flex items-center gap-2">
      <Checkbox
        id="include-inactive-accounts"
        checked={includeInactive}
        onCheckedChange={(checked) => {
          includeInactive = checked === true;
          loadData();
        }}
      />
      <Label
        for="include-inactive-accounts"
        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
      >
        Include inactive
      </Label>
    </div>
  </div>

  <!-- Error message -->
  {#if error}
    <div class="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>
  {/if}

  <!-- Loading state -->
  {#if loading}
    <div class="text-center py-8 text-gray-600">Loading accounts...</div>
  {:else}
    <!-- Accounts data table -->
    <AccountsDataTable data={accountsWithInstitutions} {columns} />
  {/if}
</div>

<!-- Modals -->
<AddEditAccountDialog
  open={showForm}
  editingAccount={editingAccount}
  loading={formLoading}
  error={formError}
  fieldErrors={formErrors}
  onOpenChange={(open) => {
    if (!open) closeForm();
  }}
  onSubmit={handleFormSubmit}
/>

<DeleteAccountDialog
  open={deleteConfirm !== null}
  loading={deleteLoading}
  onOpenChange={(open) => {
    if (!open) {
      deleteConfirm = null;
    }
  }}
  onConfirm={() => deleteConfirm !== null && handleDelete(deleteConfirm, false)}
/>
