<script lang="ts">
    import '../app.css';
    import * as Sidebar from '$lib/components/ui/sidebar';
    import * as Collapsible from '$lib/components/ui/collapsible';
    import {
        House,
        ArrowLeftRight,
        Upload,
        Settings,
        ChevronRight,
        SunIcon,
        MoonIcon,
        Wallet,
        Landmark,
        User,
        SlidersHorizontal,
        Tag,
    } from '@lucide/svelte';
    import { page } from '$app/state';
    import { Button } from '$lib/components/ui/button';
    import { toggleMode, ModeWatcher } from 'mode-watcher';
    import * as m from '$lib/paraglide/messages';
    import {
        getLocale,
        localizeHref,
        deLocalizeHref,
    } from '$lib/paraglide/runtime';
    import { Toaster, toast } from 'svelte-sonner';
    import { settingsApi } from '$lib/api/settings';
    import type { AccountDueForCheckin } from '$lib/types';
    import BalanceCheckinDialog from '$lib/components/balance-checkin-dialog.svelte';

    let { children } = $props();

    let checkinAccounts: AccountDueForCheckin[] = $state([]);
    let checkinDialogOpen = $state(false);

    $effect(() => {
        document.documentElement.lang = getLocale();
    });

    // Balance check-in reminder on mount
    $effect(() => {
        if (typeof window === 'undefined') return;
        if (sessionStorage.getItem('balance_checkin_reminded')) return;

        settingsApi
            .getAccountsDueForCheckin()
            .then((accounts: AccountDueForCheckin[]) => {
                if (accounts.length === 0) return;

                checkinAccounts = accounts;
                sessionStorage.setItem('balance_checkin_reminded', '1');

                const title = m.reminder_title({ count: accounts.length });
                const lines = accounts.map((a) => {
                    if (a.last_balance_date) {
                        return m.reminder_account_last_updated({
                            name: a.account_name,
                            date: a.last_balance_date,
                        });
                    }
                    return m.reminder_account_never_updated({
                        name: a.account_name,
                    });
                });

                toast.info(title, {
                    description: lines.join('\n'),
                    duration: 10000,
                    action: {
                        label: m.reminder_action(),
                        onClick: () => {
                            checkinDialogOpen = true;
                        },
                    },
                });
            })
            .catch(() => {
                // Reminder is non-critical; silently ignore errors
            });
    });

    const navItems = $derived([
        { href: localizeHref('/'), label: m.nav_home(), icon: House },
        {
            href: localizeHref('/transactions'),
            label: m.nav_transactions(),
            icon: ArrowLeftRight,
        },
        { href: localizeHref('/import'), label: m.nav_import(), icon: Upload },
    ]);

    const settingsSubItems = $derived([
        {
            href: localizeHref('/settings/general'),
            label: m.settings_tab_general(),
            icon: SlidersHorizontal,
        },
        {
            href: localizeHref('/settings/institutions'),
            label: m.settings_tab_institutions(),
            icon: Landmark,
        },
        {
            href: localizeHref('/settings/accounts'),
            label: m.settings_tab_accounts(),
            icon: User,
        },
        {
            href: localizeHref('/settings/categories'),
            label: m.settings_tab_categories(),
            icon: Tag,
        },
    ]);

    const isActive = (href: string) => {
        const currentPath = deLocalizeHref(page.url.pathname);
        const itemPath = deLocalizeHref(href);
        if (itemPath === '/') return currentPath === '/';
        return currentPath.startsWith(itemPath);
    };

    const isExactActive = (href: string) => {
        const currentPath = deLocalizeHref(page.url.pathname);
        const itemPath = deLocalizeHref(href);
        return currentPath === itemPath;
    };

    const settingsOpen = $derived(isActive(localizeHref('/settings')));
</script>

<ModeWatcher />
<Toaster />
<Sidebar.Provider>
    <Sidebar.Sidebar>
        <Sidebar.SidebarHeader>
            <div class="flex items-center gap-2 px-2 py-4">
                <Wallet class="size-6" />
                <h2 class="text-xl font-bold">CoinPurse</h2>
                <Button
                    class="ml-auto"
                    onclick={toggleMode}
                    variant="outline"
                    size="icon"
                >
                    <SunIcon
                        class="transition-all! h-[1.2rem] w-[1.2rem] rotate-0 scale-100 dark:-rotate-90 dark:scale-0"
                    />
                    <MoonIcon
                        class="transition-all! absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 dark:rotate-0 dark:scale-100"
                    />
                    <span class="sr-only">{m.layout_toggle_theme()}</span>
                </Button>
            </div>
        </Sidebar.SidebarHeader>

        <Sidebar.SidebarContent>
            <div class="px-4 py-2">
                <Sidebar.SidebarMenu>
                    {#each navItems as item}
                        <Sidebar.SidebarMenuItem>
                            <Sidebar.SidebarMenuButton
                                isActive={isActive(item.href)}
                                tooltipContent={item.label}
                            >
                                {#snippet child({ props })}
                                    {@const Icon = item.icon}
                                    <a href={item.href} {...props}>
                                        <Icon />
                                        <span>{item.label}</span>
                                    </a>
                                {/snippet}
                            </Sidebar.SidebarMenuButton>
                        </Sidebar.SidebarMenuItem>
                    {/each}

                    <Collapsible.Root
                        open={settingsOpen}
                        class="group/collapsible"
                    >
                        <Sidebar.SidebarMenuItem>
                            <Collapsible.Trigger>
                                {#snippet child({ props })}
                                    <Sidebar.SidebarMenuButton
                                        {...props}
                                        isActive={settingsOpen}
                                        tooltipContent={m.nav_settings()}
                                    >
                                        <Settings />
                                        <span>{m.nav_settings()}</span>
                                        <ChevronRight
                                            class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
                                        />
                                    </Sidebar.SidebarMenuButton>
                                {/snippet}
                            </Collapsible.Trigger>
                            <Collapsible.Content>
                                <Sidebar.SidebarMenuSub>
                                    {#each settingsSubItems as subItem}
                                        <Sidebar.SidebarMenuSubItem>
                                            <Sidebar.SidebarMenuSubButton
                                                isActive={isExactActive(
                                                    subItem.href
                                                )}
                                            >
                                                {#snippet child({ props })}
                                                    {@const Icon = subItem.icon}
                                                    <a
                                                        href={subItem.href}
                                                        {...props}
                                                    >
                                                        <Icon />
                                                        <span
                                                            >{subItem.label}</span
                                                        >
                                                    </a>
                                                {/snippet}
                                            </Sidebar.SidebarMenuSubButton>
                                        </Sidebar.SidebarMenuSubItem>
                                    {/each}
                                </Sidebar.SidebarMenuSub>
                            </Collapsible.Content>
                        </Sidebar.SidebarMenuItem>
                    </Collapsible.Root>
                </Sidebar.SidebarMenu>
            </div>
        </Sidebar.SidebarContent>
    </Sidebar.Sidebar>

    <Sidebar.SidebarInset>
        <main class="flex-1 p-6">
            {@render children()}
        </main>
    </Sidebar.SidebarInset>
</Sidebar.Provider>

<BalanceCheckinDialog
    open={checkinDialogOpen}
    accounts={checkinAccounts}
    onOpenChange={(open) => {
        checkinDialogOpen = open;
    }}
    onSuccess={() => {
        sessionStorage.removeItem('balance_checkin_reminded');
        toast.success(m.checkin_success());
    }}
/>
