<script lang="ts">
    import { ApiException } from '$lib/api';
    import type { Institution, Category, CategoryMapping } from '$lib/types';
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
    import * as m from '$lib/paraglide/messages';

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
                error = m.map_error_load();
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
                error = m.map_error_load_mappings();
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
            error = m.map_error_name_required();
            return;
        }

        if (row.editCategoryIds.length === 0) {
            error = m.map_error_category_required();
            return;
        }

        const institutionId = Number(selectedInstitutionId);
        error = '';
        loading = true;

        try {
            const nameChanged =
                !row.isNew && row.editName.trim() !== row.bankCategoryName;

            await categoryMappingsApi.saveGroup({
                institution_id: institutionId,
                bank_category_name: row.editName.trim(),
                coinpurse_category_ids: row.editCategoryIds.map(Number),
                old_bank_category_name: nameChanged
                    ? row.bankCategoryName
                    : undefined,
            });

            // Reload mappings from API
            await loadMappings(institutionId);
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = m.map_error_save();
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
            await categoryMappingsApi.deleteGroup({
                institution_id: Number(selectedInstitutionId),
                bank_category_name: deleteRow.bankCategoryName,
            });
            deleteRow = null;
            await loadMappings(Number(selectedInstitutionId));
        } catch (e) {
            if (e instanceof ApiException) {
                error = e.detail;
            } else {
                error = m.map_error_delete();
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
        if (catIds.length === 0) return m.map_categories_none();
        if (catIds.length <= 2) return catIds.map(getCategoryLabel).join(', ');
        return m.map_categories_count({ count: catIds.length });
    }
</script>

<div>
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold">{m.map_heading()}</h2>
        <Button onclick={addNewRow} disabled={!selectedInstitutionId}
            >{m.map_btn_add()}</Button
        >
    </div>

    <!-- Institution filter -->
    <div class="mb-6 max-w-100">
        <Combobox
            items={institutionItems}
            bind:value={selectedInstitutionId}
            placeholder={m.map_select_institution()}
            searchPlaceholder={m.map_search_institution()}
            emptyText={m.map_no_institutions()}
        />
    </div>

    <!-- Error message -->
    {#if error}
        <div class="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>
    {/if}

    {#if !selectedInstitutionId}
        <div class="text-center py-8 text-muted-foreground">
            {m.map_select_prompt()}
        </div>
    {:else if loading}
        <div class="text-center py-8 text-gray-600">{m.map_loading()}</div>
    {:else}
        <div class="rounded-md border">
            <Table.Root>
                <Table.Header>
                    <Table.Row>
                        <Table.Head class="w-[35%]">{m.map_col_bank_category()}</Table.Head>
                        <Table.Head class="w-12.5 text-center"></Table.Head>
                        <Table.Head class="w-[40%]"
                            >{m.map_col_coinpurse_categories()}</Table.Head
                        >
                        <Table.Head class="text-right">{m.map_col_actions()}</Table.Head>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {#if rows.length === 0}
                        <Table.Row>
                            <Table.Cell colspan={4} class="h-24 text-center">
                                {m.map_table_empty()}
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
                                            placeholder={m.map_bank_name_placeholder()}
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
                                            placeholder={m.map_select_categories()}
                                            searchPlaceholder={m.map_search_categories()}
                                            emptyText={m.map_no_categories()}
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
                                                title={m.map_action_save()}
                                            >
                                                <CheckIcon class="size-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onclick={() => cancelEdit(row)}
                                                title={m.map_action_cancel()}
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
                                                title={m.map_action_edit()}
                                            >
                                                <PencilIcon class="size-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onclick={() =>
                                                    (deleteRow = row)}
                                                title={m.map_action_delete()}
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
    <Dialog.Content class="sm:max-w-106.25">
        <Dialog.Header>
            <Dialog.Title>{m.map_delete_title()}</Dialog.Title>
            <Dialog.Description>
                {m.map_delete_confirm({ name: deleteRow?.bankCategoryName ?? '' })}
            </Dialog.Description>
        </Dialog.Header>

        <p class="text-yellow-800 bg-yellow-50 p-2 rounded text-sm">
            {m.map_delete_warning()}
        </p>

        <Dialog.Footer>
            <Button
                type="button"
                variant="outline"
                onclick={() => (deleteRow = null)}
            >
                {m.btn_cancel()}
            </Button>
            <Button
                variant="destructive"
                onclick={confirmDelete}
                disabled={deleteLoading}
            >
                {deleteLoading ? m.btn_deleting() : m.btn_delete()}
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
