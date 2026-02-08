<script lang="ts">
    import * as Tabs from '$lib/components/ui/tabs';
    import CategoriesTab from '../../../pages/categories/categories-tab.svelte';
    import MappingsTab from '../../../pages/categories/mappings-tab.svelte';
    import * as m from '$lib/paraglide/messages';

    let activeTab = $state('categories');
</script>

<Tabs.Root
    value={activeTab}
    onValueChange={(value) => (activeTab = value ?? 'categories')}
>
    <Tabs.List class="mb-6">
        <Tabs.Trigger value="categories">{m.cat_tab_categories()}</Tabs.Trigger>
        <Tabs.Trigger value="mappings">{m.cat_tab_mappings()}</Tabs.Trigger>
    </Tabs.List>

    <Tabs.Content value="categories">
        <CategoriesTab />
    </Tabs.Content>

    <Tabs.Content value="mappings">
        <MappingsTab />
    </Tabs.Content>
</Tabs.Root>
