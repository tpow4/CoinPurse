<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiException } from "../lib/api";
  import type {
    Institution,
    InstitutionCreate,
    InstitutionUpdate,
  } from "../lib/types";
  import * as Dialog from "$lib/components/ui/dialog";
  import * as Field from "$lib/components/ui/field";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import InstitutionsDataTable from "./institutions/institutions-data-table.svelte";
  import { createColumns } from "./institutions/columns";

  // State
  let institutions: Institution[] = [];
  let loading = false;
  let error = "";
  let searchTerm = "";
  let includeInactive = false;

  // Create columns with callbacks
  const columns = createColumns({
    onEdit: openEditForm,
    onDelete: (institution) => (deleteConfirm = institution.institution_id),
  });

  // Form state
  let showForm = false;
  let editingId: number | null = null;
  let formData = {
    name: "",
  };
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

  // Load institutions from API
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

  // Search institutions
  async function handleSearch() {
    if (!searchTerm.trim()) {
      loadInstitutions();
      return;
    }

    loading = true;
    error = "";
    try {
      institutions = await api.institutions.search(searchTerm);
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

  // Validate form
  function validateForm(): boolean {
    formErrors.name = "";

    if (!formData.name.trim()) {
      formErrors.name = "Institution name is required";
      return false;
    }

    if (formData.name.length > 100) {
      formErrors.name = "Name is too long (max 100 characters)";
      return false;
    }

    return true;
  }

  // Open form for creating new institution
  function openCreateForm() {
    editingId = null;
    formData = { name: "" };
    formErrors = { name: "" };
    formError = "";
    showForm = true;
  }

  // Open form for editing institution
  function openEditForm(institution: Institution) {
    editingId = institution.institution_id;
    formData = { name: institution.name };
    formErrors = { name: "" };
    formError = "";
    showForm = true;
  }

  // Close form
  function closeForm() {
    showForm = false;
    editingId = null;
    formData = { name: "" };
    formErrors = { name: "" };
    formError = "";
  }

  // Submit form (create or update)
  async function handleSubmit() {
    formError = "";

    if (!validateForm()) {
      return;
    }

    formLoading = true;
    try {
      if (editingId !== null) {
        // Update existing
        const updateData: InstitutionUpdate = {
          name: formData.name,
        };
        await api.institutions.update(editingId, updateData);
      } else {
        // Create new
        const createData: InstitutionCreate = {
          name: formData.name,
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

  // Delete institution
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

  // Toggle inactive filter
  function toggleInactive() {
    includeInactive = !includeInactive;
    loadInstitutions();
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
      <input
        class="max-w-full"
        type="text"
        placeholder="Search institutions..."
        bind:value={searchTerm}
        on:input={handleSearch}
      />
    </div>
    <label class="checkbox-label">
      <input
        type="checkbox"
        bind:checked={includeInactive}
        on:change={toggleInactive}
      />
      Include inactive
    </label>
  </div>

  <!-- Error message -->
  {#if error}
    <div class="error-message">{error}</div>
  {/if}

  <!-- Loading state -->
  {#if loading}
    <div class="loading">Loading institutions...</div>
  {:else if institutions.length === 0}
    <div class="empty-state">
      <p>No institutions found</p>
      <Button onclick={openCreateForm}>Add your first institution</Button>
    </div>
  {:else}
    <!-- Institutions data table -->
    <InstitutionsDataTable data={institutions} {columns} />
  {/if}
</div>

<!-- Create/Edit Form Modal -->
<Dialog.Root
  open={showForm}
  onOpenChange={(open) => {
    if (!open) closeForm();
  }}
>
  <Dialog.Content class="sm:max-w-[425px]">
    <Dialog.Header>
      <Dialog.Title
        >{editingId !== null
          ? "Edit Institution"
          : "Add Institution"}</Dialog.Title
      >
      <Dialog.Description>
        {editingId !== null
          ? "Update the institution details below."
          : "Add a new financial institution to track your accounts."}
      </Dialog.Description>
    </Dialog.Header>

    <form on:submit|preventDefault={handleSubmit}>
      {#if formError}
        <div class="error-message">{formError}</div>
      {/if}

      <Field.Field data-invalid={formErrors.name ? true : undefined}>
        <Field.Label for="institution_name">Institution Name</Field.Label>
        <Input
          type="text"
          id="institution_name"
          bind:value={formData.name}
          placeholder="e.g., Chase Bank"
          aria-invalid={formErrors.name ? true : undefined}
        />
        {#if formErrors.name}
          <Field.Error>{formErrors.name}</Field.Error>
        {/if}
      </Field.Field>

      <Dialog.Footer>
        <Button type="button" variant="outline" onclick={closeForm}>
          Cancel
        </Button>
        <Button type="submit" disabled={formLoading}>
          {formLoading ? "Saving..." : editingId !== null ? "Update" : "Create"}
        </Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>

<!-- Delete Confirmation Modal -->
<Dialog.Root
  open={deleteConfirm !== null}
  onOpenChange={(open) => {
    if (!open) deleteConfirm = null;
  }}
>
  <Dialog.Content class="sm:max-w-[425px]">
    <Dialog.Header>
      <Dialog.Title>Delete Institution</Dialog.Title>
      <Dialog.Description>
        Are you sure you want to delete this institution?
      </Dialog.Description>
    </Dialog.Header>

    <p class="warning">This will perform a soft delete (set to inactive).</p>

    <Dialog.Footer>
      <Button
        type="button"
        variant="outline"
        onclick={() => (deleteConfirm = null)}
      >
        Cancel
      </Button>
      <Button
        variant="destructive"
        onclick={() => deleteConfirm !== null && handleDelete(deleteConfirm, false)}
        disabled={deleteLoading}
      >
        {deleteLoading ? "Deleting..." : "Delete"}
      </Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>

<style>
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    user-select: none;
  }

  .checkbox-label input[type="checkbox"] {
    cursor: pointer;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    background: white;
    border-radius: 8px;
    border: 1px dashed #ddd;
  }

  .empty-state p {
    color: #666;
    margin-bottom: 1rem;
  }

  .error-message {
    background: #fee;
    color: #c33;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .warning {
    color: #856404;
    background: #fff3cd;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }
</style>
