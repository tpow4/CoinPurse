<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiException } from '../lib/api';
  import type { Institution, InstitutionCreate, InstitutionUpdate } from '../lib/types';

  // State
  let institutions: Institution[] = [];
  let loading = false;
  let error = '';
  let searchTerm = '';
  let includeInactive = false;

  // Form state
  let showForm = false;
  let editingId: number | null = null;
  let formData = {
    name: ''
  };
  let formError = '';
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
    error = '';
    try {
      institutions = await api.institutions.getAll(includeInactive);
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = 'Failed to load institutions';
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
    error = '';
    try {
      institutions = await api.institutions.search(searchTerm);
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = 'Search failed';
      }
    } finally {
      loading = false;
    }
  }

  // Open form for creating new institution
  function openCreateForm() {
    editingId = null;
    formData = { name: '' };
    formError = '';
    showForm = true;
  }

  // Open form for editing institution
  function openEditForm(institution: Institution) {
    editingId = institution.institution_id;
    formData = { name: institution.name };
    formError = '';
    showForm = true;
  }

  // Close form
  function closeForm() {
    showForm = false;
    editingId = null;
    formData = { name: '' };
    formError = '';
  }

  // Submit form (create or update)
  async function handleSubmit() {
    formError = '';

    if (!formData.name.trim()) {
      formError = 'Institution name is required';
      return;
    }

    formLoading = true;
    try {
      if (editingId !== null) {
        // Update existing
        const updateData: InstitutionUpdate = {
          name: formData.name
        };
        await api.institutions.update(editingId, updateData);
      } else {
        // Create new
        const createData: InstitutionCreate = {
          name: formData.name
        };
        await api.institutions.create(createData);
      }

      closeForm();
      loadInstitutions();
    } catch (e) {
      if (e instanceof ApiException) {
        formError = e.detail;
      } else {
        formError = 'Failed to save institution';
      }
    } finally {
      formLoading = false;
    }
  }

  // Delete institution
  async function handleDelete(id: number, hardDelete = false) {
    deleteLoading = true;
    error = '';
    try {
      await api.institutions.delete(id, hardDelete);
      deleteConfirm = null;
      loadInstitutions();
    } catch (e) {
      if (e instanceof ApiException) {
        error = e.detail;
      } else {
        error = 'Failed to delete institution';
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

<div class="page">
  <div class="page-header">
    <h1>Institutions</h1>
    <button on:click={openCreateForm}>+ Add Institution</button>
  </div>

  <!-- Search and filters -->
  <div class="controls">
    <div class="search-box">
      <input
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
      <button on:click={openCreateForm}>Add your first institution</button>
    </div>
  {:else}
    <!-- Institutions table -->
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Status</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each institutions as institution}
          <tr class:inactive={!institution.is_active}>
            <td>{institution.name}</td>
            <td>
              <span class="status" class:active={institution.is_active}>
                {institution.is_active ? 'Active' : 'Inactive'}
              </span>
            </td>
            <td>{new Date(institution.created_at).toLocaleDateString()}</td>
            <td>
              <div class="actions">
                <button class="btn-edit" on:click={() => openEditForm(institution)}>
                  Edit
                </button>
                <button
                  class="btn-delete"
                  on:click={() => deleteConfirm = institution.institution_id}
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<!-- Create/Edit Form Modal -->
{#if showForm}
  <div class="modal-backdrop" on:click={closeForm}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingId !== null ? 'Edit Institution' : 'Add Institution'}</h2>
        <button class="close-btn" on:click={closeForm}>&times;</button>
      </div>

      <form on:submit|preventDefault={handleSubmit}>
        {#if formError}
          <div class="error-message">{formError}</div>
        {/if}

        <div class="form-group">
          <label for="institution_name">Institution Name</label>
          <input
            type="text"
            id="institution_name"
            bind:value={formData.name}
            placeholder="e.g., Chase Bank"
            required
          />
        </div>

        <div class="form-actions">
          <button type="button" class="btn-secondary" on:click={closeForm}>
            Cancel
          </button>
          <button type="submit" disabled={formLoading}>
            {formLoading ? 'Saving...' : (editingId !== null ? 'Update' : 'Create')}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if deleteConfirm !== null}
  <div class="modal-backdrop" on:click={() => deleteConfirm = null}>
    <div class="modal modal-small" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Delete Institution</h2>
        <button class="close-btn" on:click={() => deleteConfirm = null}>&times;</button>
      </div>

      <p>Are you sure you want to delete this institution?</p>
      <p class="warning">This will perform a soft delete (set to inactive).</p>

      <div class="form-actions">
        <button class="btn-secondary" on:click={() => deleteConfirm = null}>
          Cancel
        </button>
        <button
          class="btn-delete"
          on:click={() => handleDelete(deleteConfirm, false)}
          disabled={deleteLoading}
        >
          {deleteLoading ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .page {
    padding: 2rem;
    max-width: 1200px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .page-header h1 {
    margin: 0;
    font-size: 2rem;
  }

  .controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    align-items: center;
  }

  .search-box {
    flex: 1;
    max-width: 400px;
  }

  .search-box input {
    width: 100%;
  }

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

  table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  tr.inactive {
    opacity: 0.6;
  }

  .status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.875rem;
    background: #e0e0e0;
    color: #666;
  }

  .status.active {
    background: #d4edda;
    color: #155724;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-edit,
  .btn-delete {
    padding: 0.4rem 0.8rem;
    font-size: 0.875rem;
  }

  .btn-edit {
    background: #6c757d;
  }

  .btn-edit:hover {
    background: #5a6268;
  }

  .btn-delete {
    background: #dc3545;
  }

  .btn-delete:hover {
    background: #c82333;
  }

  .btn-secondary {
    background: #6c757d;
  }

  .btn-secondary:hover {
    background: #5a6268;
  }

  /* Modal styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .modal-small {
    max-width: 400px;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 2rem;
    color: #999;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-btn:hover {
    color: #333;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .form-group input {
    width: 100%;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .warning {
    color: #856404;
    background: #fff3cd;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }
</style>
