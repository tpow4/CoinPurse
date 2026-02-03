<script lang="ts">
    import { ApiException } from '$lib/api';
    import type {
        Institution,
        Category,
        CategoryMapping,
        CategoryMappingCreate,
    } from '$lib/types';
    import { institutionsApi } from '$lib/api/institutions';
    import { categoriesApi } from '$lib/api/categories';
    import { categoryMappingsApi } from '$lib/api/category-mappings';
    import { Combobox, MultiCombobox } from '$lib/components/ui/combobox';
    import type { ComboboxItem } from '$lib/components/ui/combobox/combobox.svelte';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import * as Table from '$lib/components/ui/table';
    import * as Dialog from '$lib/components/ui/dialog';
    import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
    import PencilIcon from '@lucide/svelte/icons/pencil';
    import TrashIcon from '@lucide/svelte/icons/trash-2';
    import CheckIcon from '@lucide/svelte/icons/check';
    import XIcon from '@lucide/svelte/icons/x';

    // --- Data state ---
    let institutions = $state<Institution[]>([]);
    let categories = $state<Category[]>([]);
    let mappings = $state<CategoryMapping[]>([]);
    let loading = $state(false);
    let error = $state('');

    // --- Institution filter ---
    let selectedInstitutionId = $state('');

    // --- Grouped mapping rows ---
    interface MappingRow {
        bankCategoryName: string;
        categoryIds: string[];
        mappingIds: number[]; // API mapping IDs for this group
        isEditing: boolean;
        isNew: boolean;
        editName: string;
        editCategoryIds: string[];
    }

    let rows = $state<MappingRow[]>([]);

    // --- Delete state ---
    let deleteRow = $state<MappingRow | null>(null);
    let deleteLoading = $state(false);
    const deleteDialogOpen = $derived(deleteRow !== null);

    // --- Combobox items ---
    const institutionItems = $derived<ComboboxItem[]>(
        institutions.map((i) => ({
            value: String(i.institution_id),
            label: i.name,
        }))
    );

    const categoryItems = $derived<ComboboxItem[]>(
        categories.map((c) => ({
            value: String(c.category_id),
            label: c.name,
        }))
    );

    // --- Load institutions and categories on mount ---
    $effect(() => {
        loadInitialData();
    });

    // --- Load mappings when institution changes ---
    $effect(() => {
        if (selectedInstitutionId) {
            loadMappings(Number(selectedInstitutionId));
        } else {
            mappings = [];
            rows = [];
        }
    });

    async function loadInitialData() {
        try {
            [institutions, categories] = await Promise.all([
                institutionsApi.getAll(false),
                categoriesApi.getAll(false),
            ]);
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to load data';
            }
        }
    }

    let loadMappingsVersion = 0;

    async function loadMappings(institutionId: number) {
        const version = ++loadMappingsVersion;
        loading = true;
        error = '';
        try {
            const result = await categoryMappingsApi.getAll(institutionId);
            if (version !== loadMappingsVersion) return;
            mappings = result;
            rows = groupMappings(mappings);
        } catch (e) {
            if (version !== loadMappingsVersion) return;
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to load mappings';
            }
        } finally {
            if (version === loadMappingsVersion) {
                loading = false;
            }
        }
    }

    function groupMappings(flat: CategoryMapping[]): MappingRow[] {
        const groups = new Map<
            string,
            { categoryIds: string[]; mappingIds: number[] }
        >();

        for (const m of flat) {
            const existing = groups.get(m.bank_category_name);
            if (existing) {
                existing.categoryIds.push(String(m.coinpurse_category_id));
                existing.mappingIds.push(m.mapping_id);
            } else {
                groups.set(m.bank_category_name, {
                    categoryIds: [String(m.coinpurse_category_id)],
                    mappingIds: [m.mapping_id],
                });
            }
        }

        return Array.from(groups.entries()).map(([name, data]) => ({
            bankCategoryName: name,
            categoryIds: data.categoryIds,
            mappingIds: data.mappingIds,
            isEditing: false,
            isNew: false,
            editName: name,
            editCategoryIds: [...data.categoryIds],
        }));
    }

    function addNewRow() {
        rows = [
            {
                bankCategoryName: '',
                categoryIds: [],
                mappingIds: [],
                isEditing: true,
                isNew: true,
                editName: '',
                editCategoryIds: [],
            },
            ...rows,
        ];
    }

    function startEdit(row: MappingRow) {
        row.isEditing = true;
        row.editName = row.bankCategoryName;
        row.editCategoryIds = [...row.categoryIds];
    }

    function cancelEdit(row: MappingRow) {
        if (row.isNew) {
            rows = rows.filter((r) => r !== row);
        } else {
            row.isEditing = false;
            row.editName = row.bankCategoryName;
            row.editCategoryIds = [...row.categoryIds];
        }
    }

    async function saveRow(row: MappingRow) {
        if (!row.editName.trim()) {
            error = 'Bank category name is required';
            return;
        }

        if (row.editCategoryIds.length === 0) {
            error = 'At least one CoinPurse category is required';
            return;
        }

        const institutionId = Number(selectedInstitutionId);
        error = '';
        loading = true;

        try {
            if (row.isNew) {
                // Create all new mappings
                for (const catId of row.editCategoryIds) {
                    const createData: CategoryMappingCreate = {
                        institution_id: institutionId,
                        bank_category_name: row.editName.trim(),
                        coinpurse_category_id: Number(catId),
                    };
                    await categoryMappingsApi.create(createData);
                }
            } else {
                // Diff-based save
                const oldCatIds = new Set(row.categoryIds);
                const newCatIds = new Set(row.editCategoryIds);
                const nameChanged =
                    row.editName.trim() !== row.bankCategoryName;

                // Delete removed categories
                for (let i = 0; i < row.categoryIds.length; i++) {
                    if (!newCatIds.has(row.categoryIds[i])) {
                        await categoryMappingsApi.delete(
                            row.mappingIds[i],
                            true
                        );
                    }
                }

                // Create added categories
                for (const catId of row.editCategoryIds) {
                    if (!oldCatIds.has(catId)) {
                        const createData: CategoryMappingCreate = {
                            institution_id: institutionId,
                            bank_category_name: row.editName.trim(),
                            coinpurse_category_id: Number(catId),
                        };
                        await categoryMappingsApi.create(createData);
                    }
                }

                // Update bank_category_name on remaining mappings if name changed
                if (nameChanged) {
                    for (let i = 0; i < row.categoryIds.length; i++) {
                        if (newCatIds.has(row.categoryIds[i])) {
                            await categoryMappingsApi.update(
                                row.mappingIds[i],
                                {
                                    bank_category_name: row.editName.trim(),
                                }
                            );
                        }
                    }
                }
            }

            // Reload mappings from API
            await loadMappings(institutionId);
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to save mapping';
            }
        } finally {
            loading = false;
        }
    }

    async function confirmDelete() {
        if (!deleteRow || !selectedInstitutionId) return;

        deleteLoading = true;
        error = '';
        try {
            // Hard delete all mappings in this group
            for (const mappingId of deleteRow.mappingIds) {
                await categoryMappingsApi.delete(mappingId, true);
            }
            deleteRow = null;
            await loadMappings(Number(selectedInstitutionId));
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = 'Failed to delete mapping';
            }
        } finally {
            deleteLoading = false;
        }
    }

    function getCategoryLabel(catId: string): string {
        const cat = categories.find((c) => String(c.category_id) === catId);
        return cat?.name ?? catId;
    }

    function formatCategoryLabels(catIds: string[]): string {
        if (catIds.length === 0) return 'None';
        if (catIds.length <= 2) return catIds.map(getCategoryLabel).join(', ');
        return `${catIds.length} categories`;
    }
</script>

<div>
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold">Category Mappings</h2>
        <Button onclick={addNewRow} disabled={!selectedInstitutionId}
            >+ Add Mapping</Button
        >
    </div>

    <!-- Institution filter -->
    <div class="mb-6 max-w-[400px]">
        <Combobox
            items={institutionItems}
            bind:value={selectedInstitutionId}
            placeholder="Select institution..."
            searchPlaceholder="Search institutions..."
            emptyText="No institutions found."
        />
    </div>

    <!-- Error message -->
    {#if error}
        <div class="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>
    {/if}

    {#if !selectedInstitutionId}
        <div class="text-center py-8 text-muted-foreground">
            Select an institution to view and manage its category mappings.
        </div>
    {:else if loading}
        <div class="text-center py-8 text-gray-600">Loading mappings...</div>
    {:else}
        <div class="rounded-md border">
            <Table.Root>
                <Table.Header>
                    <Table.Row>
                        <Table.Head class="w-[35%]">Bank Category</Table.Head>
                        <Table.Head class="w-[50px] text-center"></Table.Head>
                        <Table.Head class="w-[40%]"
                            >CoinPurse Categories</Table.Head
                        >
                        <Table.Head class="text-right">Actions</Table.Head>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {#if rows.length === 0}
                        <Table.Row>
                            <Table.Cell colspan={4} class="h-24 text-center">
                                No mappings for this institution.
                            </Table.Cell>
                        </Table.Row>
                    {:else}
                        {#each rows as row (row.isNew ? `new-${rows.indexOf(row)}` : row.bankCategoryName)}
                            <Table.Row>
                                <!-- Bank Category Name -->
                                <Table.Cell>
                                    {#if row.isEditing}
                                        <Input
                                            type="text"
                                            bind:value={row.editName}
                                            placeholder="Bank category name"
                                            class="h-9"
                                        />
                                    {:else}
                                        {row.bankCategoryName}
                                    {/if}
                                </Table.Cell>

                                <!-- Arrow -->
                                <Table.Cell class="text-center">
                                    <ArrowRightIcon
                                        class="size-4 mx-auto text-muted-foreground"
                                    />
                                </Table.Cell>

                                <!-- CoinPurse Categories -->
                                <Table.Cell>
                                    {#if row.isEditing}
                                        <MultiCombobox
                                            items={categoryItems}
                                            bind:values={row.editCategoryIds}
                                            placeholder="Select categories..."
                                            searchPlaceholder="Search categories..."
                                            emptyText="No categories found."
                                        />
                                    {:else}
                                        {formatCategoryLabels(row.categoryIds)}
                                    {/if}
                                </Table.Cell>

                                <!-- Actions -->
                                <Table.Cell class="text-right">
                                    {#if row.isEditing}
                                        <div class="flex gap-1 justify-end">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onclick={() => saveRow(row)}
                                                title="Save"
                                            >
                                                <CheckIcon class="size-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onclick={() => cancelEdit(row)}
                                                title="Cancel"
                                            >
                                                <XIcon class="size-4" />
                                            </Button>
                                        </div>
                                    {:else}
                                        <div class="flex gap-1 justify-end">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onclick={() => startEdit(row)}
                                                title="Edit"
                                            >
                                                <PencilIcon class="size-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onclick={() =>
                                                    (deleteRow = row)}
                                                title="Delete"
                                            >
                                                <TrashIcon class="size-4" />
                                            </Button>
                                        </div>
                                    {/if}
                                </Table.Cell>
                            </Table.Row>
                        {/each}
                    {/if}
                </Table.Body>
            </Table.Root>
        </div>
    {/if}
</div>

<!-- Delete confirmation -->
<Dialog.Root
    open={deleteDialogOpen}
    onOpenChange={(open) => {
        if (!open) deleteRow = null;
    }}
>
    <Dialog.Content class="sm:max-w-[425px]">
        <Dialog.Header>
            <Dialog.Title>Delete Mapping</Dialog.Title>
            <Dialog.Description>
                Are you sure you want to delete the mapping for "{deleteRow?.bankCategoryName}"?
            </Dialog.Description>
        </Dialog.Header>

        <p class="text-yellow-800 bg-yellow-50 p-2 rounded text-sm">
            This will permanently delete all category mappings for this bank
            category name.
        </p>

        <Dialog.Footer>
            <Button
                type="button"
                variant="outline"
                onclick={() => (deleteRow = null)}
            >
                Cancel
            </Button>
            <Button
                variant="destructive"
                onclick={confirmDelete}
                disabled={deleteLoading}
            >
                {deleteLoading ? 'Deleting...' : 'Delete'}
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
