<script lang="ts">
    import * as Tabs from '$lib/components/ui/tabs';
    import InstitutionsTab from '../../pages/admin/institutions-tab.svelte';
    import AccountsTab from '../../pages/admin/accounts-tab.svelte';
    import GeneralTab from '../../pages/admin/general-tab.svelte';

    // State
    let activeTab = $state('general');
</script>

<div class="p-8 max-w-[1400px] mx-auto">
    <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">Admin</h1>
        <p class="text-muted-foreground">Manage institutions and accounts</p>
    </div>

    <Tabs.Root
        value={activeTab}
        onValueChange={(value) => (activeTab = value ?? 'institutions')}
    >
        <Tabs.List class="mb-6">
            <Tabs.Trigger value="general">General</Tabs.Trigger>
            <Tabs.Trigger value="institutions">Institutions</Tabs.Trigger>
            <Tabs.Trigger value="accounts">Accounts</Tabs.Trigger>
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
