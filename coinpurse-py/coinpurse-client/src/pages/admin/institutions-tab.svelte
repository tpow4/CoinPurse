<script lang="ts">
  import { ApiException } from "../../lib/api";
  import type {
    Institution,
    InstitutionCreate,
    InstitutionUpdate,
  } from "../../lib/types";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import { Label } from "$lib/components/ui/label";
  import { Checkbox } from "$lib/components/ui/checkbox";
  import InstitutionsDataTable from "../institutions/institutions-data-table.svelte";
  import DeleteInstitutionDialog from "../institutions/delete-institution-dialog.svelte";
  import AddEditInstitutionDialog from "../institutions/add-edit-institution-dialog.svelte";
  import { createColumns } from "../institutions/columns";
  import { institutionsApi } from "$lib/api/institutions";

  // State
  let institutions = $state<Institution[]>([]);
  let loading = $state(false);
  let error = $state("");
  let searchTerm = $state("");
  let includeInactive = $state(false);

  // Add/edit state
  let showForm = $state(false);
  let editingInstitution = $state<Institution | null>(null);
  let formErrors = $state({
    name: "",
  });
  let formError = $state("");
  let formLoading = $state(false);

  // Delete state
  let deleteConfirm = $state<number | null>(null);
  let deleteLoading = $state(false);

  const deleteDialogOpen = $derived(deleteConfirm !== null);

  // Load institutions on mount and whenever includeInactive changes
  $effect(() => {
    includeInactive;
    loadInstitutions();
  });

  // Create grid columns with callbacks
  const columns = createColumns({
    onEdit: openEditForm,
    onDelete: (institution) => (deleteConfirm = institution.institution_id),
  });

  async function loadInstitutions() {
    loading = true;
    error = "";
    try {
      institutions = await institutionsApi.getAll(includeInactive);
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = "Failed to load institutions";
      }
    } finally {
      loading = false;
    }
  }

  async function handleSearch() {
    if (!searchTerm.trim()) {
      loadInstitutions();
      return;
    }

    loading = true;
    error = "";
    try {
      institutions = await institutionsApi.search(searchTerm, includeInactive);
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

  function validateForm(name: string): boolean {
    formErrors.name = "";

    if (!name.trim()) {
      formErrors.name = "Institution name is required";
      return false;
    }

    if (name.length > 100) {
      formErrors.name = "Name is too long (max 100 characters)";
      return false;
    }

    return true;
  }

  function openCreateForm() {
    editingInstitution = null;
    formErrors = { name: "" };
    formError = "";
    showForm = true;
  }

  function openEditForm(institution: Institution) {
    editingInstitution = institution;
    formErrors = { name: "" };
    formError = "";
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingInstitution = null;
    formErrors = { name: "" };
    formError = "";
  }

  async function handleFormSubmit(data: { name: string }) {
    formError = "";

    if (!validateForm(data.name)) {
      return;
    }

    formLoading = true;
    try {
      if (editingInstitution !== null) {
        // Update existing
        const updateData: InstitutionUpdate = {
          name: data.name,
        };
        await institutionsApi.update(editingInstitution.institution_id, updateData);
      } else {
        // Create new
        const createData: InstitutionCreate = {
          name: data.name,
        };
        await institutionsApi.create(createData);
      }

      closeForm();
      loadInstitutions();
    } catch (e) {
      if (e instanceof ApiException) {
        formError = e.detail;
      } else {
        formError = "Failed to save institution";
      }
    } finally {
      formLoading = false;
    }
  }

  async function handleDelete(id: number, hardDelete = false) {
    deleteLoading = true;
    error = "";
    try {
      await institutionsApi.delete(id, hardDelete);
      deleteConfirm = null;
      loadInstitutions();
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = "Failed to delete institution";
      }
    } finally {
      deleteLoading = false;
    }
  }
</script>

<div>
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold">Institutions</h2>
    <Button onclick={openCreateForm}>+ Add Institution</Button>
  </div>

  <!-- Search and filters -->
  <div class="flex gap-4 mb-6 items-center">
    <div class="flex-1 max-w-[400px]">
      <Input
        type="text"
        placeholder="Search institutions..."
        bind:value={searchTerm}
        oninput={handleSearch}
      />
    </div>
    <div class="flex items-center gap-2">
      <Checkbox
        id="include-inactive"
        checked={includeInactive}
        onCheckedChange={(checked) => {
          includeInactive = checked === true;
        }}
      />
      <Label
        for="include-inactive"
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
    <div class="text-center py-8 text-gray-600">Loading institutions...</div>
  {:else}
    <!-- Institutions data table -->
    <InstitutionsDataTable data={institutions} {columns} />
  {/if}
</div>

<!-- Modals -->
<AddEditInstitutionDialog
  open={showForm}
  editingInstitution={editingInstitution}
  loading={formLoading}
  error={formError}
  fieldErrors={formErrors}
  onOpenChange={(open) => {
    if (!open) closeForm();
  }}
  onSubmit={handleFormSubmit}
/>

<DeleteInstitutionDialog
  open={deleteDialogOpen}
  loading={deleteLoading}
  onOpenChange={(open) => {
    if (!open) {
      deleteConfirm = null;
    }
  }}
  onConfirm={() => deleteConfirm !== null && handleDelete(deleteConfirm, false)}
/>
