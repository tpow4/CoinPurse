<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiException } from "../lib/api";
  import type {
    Institution,
    InstitutionCreate,
    InstitutionUpdate,
  } from "../lib/types";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import { Label } from "$lib/components/ui/label";
  import { Checkbox } from "$lib/components/ui/checkbox";
  import InstitutionsDataTable from "./institutions/institutions-data-table.svelte";
  import DeleteInstitutionDialog from "./institutions/delete-institution-dialog.svelte";
  import AddEditInstitutionDialog from "./institutions/add-edit-institution-dialog.svelte";
  import { createColumns } from "./institutions/columns";

  // State
  let institutions: Institution[] = [];
  let loading = false;
  let error = "";
  let searchTerm = "";
  let includeInactive = false;

  // Add/edit state
  let showForm = false;
  let editingInstitution: Institution | null = null;
  let formErrors = {
    name: "",
  };
  let formError = "";
  let formLoading = false;

  // Delete state
  let deleteConfirm: number | null = null;
  let deleteLoading = false;

  // Load institutions on mount
  onMount(() => {
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
      institutions = await api.institutions.getAll(includeInactive);
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
      institutions = await api.institutions.search(searchTerm, includeInactive);
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
        await api.institutions.update(editingInstitution.institution_id, updateData);
      } else {
        // Create new
        const createData: InstitutionCreate = {
          name: data.name,
        };
        await api.institutions.create(createData);
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
      await api.institutions.delete(id, hardDelete);
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

<div class="p-8 max-w-[1200px] mx-auto">
  <div class="flex justify-between items-center mb-8">
    <h1 class="m-0 text-2xl font-semibold">Institutions</h1>
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
          loadInstitutions();
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
  open={deleteConfirm !== null}
  loading={deleteLoading}
  onOpenChange={(open) => {
    if (!open) {
        deleteConfirm = null;
    } 
  }}
  onConfirm={() => deleteConfirm !== null && handleDelete(deleteConfirm, false)}
/>
