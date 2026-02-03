<script lang="ts">
    import { ApiException } from '$lib/api';
    import type { Category, CategoryCreate, CategoryUpdate } from '$lib/types';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import { Label } from '$lib/components/ui/label';
    import { Checkbox } from '$lib/components/ui/checkbox';
    import CategoriesDataTable from './categories-data-table.svelte';
    import DeleteCategoryDialog from './delete-category-dialog.svelte';
    import AddEditCategoryDialog from './add-edit-category-dialog.svelte';
    import { createColumns } from './categories-columns';
    import { categoriesApi } from '$lib/api/categories';

    // State
    let categories = $state<Category[]>([]);
    let loading = $state(false);
    let error = $state('');
    let searchTerm = $state('');
    let includeInactive = $state(false);

    // Add/edit state
    let showForm = $state(false);
    let editingCategory = $state<Category | null>(null);
    let formErrors = $state({
        name: '',
    });
    let formError = $state('');
    let formLoading = $state(false);

    // Delete state
    let deleteConfirm = $state<number | null>(null);
    let deleteLoading = $state(false);

    const deleteDialogOpen = $derived(deleteConfirm !== null);

    // Load categories on mount and whenever includeInactive changes
    $effect(() => {
        includeInactive;
        loadCategories();
    });

    // Create grid columns with callbacks
    const columns = createColumns({
        onEdit: openEditForm,
        onDelete: (category) => (deleteConfirm = category.category_id),
    });

    async function loadCategories() {
        loading = true;
        error = '';
        try {
            categories = await categoriesApi.getAll(includeInactive);
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to load categories';
            }
        } finally {
            loading = false;
        }
    }

    async function handleSearch() {
        if (!searchTerm.trim()) {
            loadCategories();
            return;
        }

        loading = true;
        error = '';
        try {
            categories = await categoriesApi.search({
                q: searchTerm,
                include_inactive: includeInactive,
            });
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

    function validateForm(name: string): boolean {
        formErrors.name = '';

        if (!name.trim()) {
            formErrors.name = 'Category name is required';
            return false;
        }

        if (name.length > 100) {
            formErrors.name = 'Name is too long (max 100 characters)';
            return false;
        }

        return true;
    }

    function openCreateForm() {
        editingCategory = null;
        formErrors = { name: '' };
        formError = '';
        showForm = true;
    }

    function openEditForm(category: Category) {
        editingCategory = category;
        formErrors = { name: '' };
        formError = '';
        showForm = true;
    }

    function closeForm() {
        showForm = false;
        editingCategory = null;
        formErrors = { name: '' };
        formError = '';
    }

    async function handleFormSubmit(data: { name: string }) {
        formError = '';

        if (!validateForm(data.name)) {
            return;
        }

        formLoading = true;
        try {
            if (editingCategory !== null) {
                const updateData: CategoryUpdate = {
                    name: data.name,
                };
                await categoriesApi.update(
                    editingCategory.category_id,
                    updateData
                );
            } else {
                const createData: CategoryCreate = {
                    name: data.name,
                };
                await categoriesApi.create(createData);
            }

            closeForm();
            loadCategories();
        } catch (e) {
            if (e instanceof ApiException) {
                formError = e.detail;
            } else {
                formError = 'Failed to save category';
            }
        } finally {
            formLoading = false;
        }
    }

    async function handleDelete(id: number, hardDelete = false) {
        deleteLoading = true;
        error = '';
        try {
            await categoriesApi.delete(id, hardDelete);
            deleteConfirm = null;
            loadCategories();
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to delete category';
            }
        } finally {
            deleteLoading = false;
        }
    }
</script>

<div>
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold">Categories</h2>
        <Button onclick={openCreateForm}>+ Add Category</Button>
    </div>

    <!-- Search and filters -->
    <div class="flex gap-4 mb-6 items-center">
        <div class="flex-1 max-w-100">
            <Input
                type="text"
                placeholder="Search categories..."
                bind:value={searchTerm}
                oninput={handleSearch}
                aria-label="Search categories"
            />
        </div>
        <div class="flex items-center gap-2">
            <Checkbox
                id="include-inactive-categories"
                checked={includeInactive}
                onCheckedChange={(checked) => {
                    includeInactive = checked === true;
                }}
            />
            <Label
                for="include-inactive-categories"
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
        <div class="text-center py-8 text-gray-600">Loading categories...</div>
    {:else}
        <CategoriesDataTable data={categories} {columns} />
    {/if}
</div>

<!-- Modals -->
<AddEditCategoryDialog
    open={showForm}
    {editingCategory}
    loading={formLoading}
    error={formError}
    fieldErrors={formErrors}
    onOpenChange={(open) => {
        if (!open) closeForm();
    }}
    onSubmit={handleFormSubmit}
/>

<DeleteCategoryDialog
    open={deleteDialogOpen}
    loading={deleteLoading}
    onOpenChange={(open) => {
        if (!open) {
            deleteConfirm = null;
        }
    }}
    onConfirm={() =>
        deleteConfirm !== null && handleDelete(deleteConfirm, false)}
/>
