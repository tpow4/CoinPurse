<script lang="ts">
    import * as Tabs from '$lib/components/ui/tabs';
    import InstitutionsTab from '../../pages/admin/institutions-tab.svelte';
    import AccountsTab from '../../pages/admin/accounts-tab.svelte';
    import GeneralTab from '../../pages/admin/general-tab.svelte';
    import * as m from '$lib/paraglide/messages';

    let activeTab = $state('general');
</script>

<div class="p-8 max-w-350 mx-auto">
    <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">{m.admin_title()}</h1>
        <p class="text-muted-foreground">{m.admin_description()}</p>
    </div>

    <Tabs.Root
        value={activeTab}
        onValueChange={(value) => (activeTab = value ?? 'institutions')}
    >
        <Tabs.List class="mb-6">
            <Tabs.Trigger value="general">{m.admin_tab_general()}</Tabs.Trigger>
            <Tabs.Trigger value="institutions">{m.admin_tab_institutions()}</Tabs.Trigger>
            <Tabs.Trigger value="accounts">{m.admin_tab_accounts()}</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="general">
            <GeneralTab />
        </Tabs.Content>

        <Tabs.Content value="institutions">
            <InstitutionsTab />
        </Tabs.Content>

        <Tabs.Content value="accounts">
            <AccountsTab />
        </Tabs.Content>
    </Tabs.Root>
</div>
