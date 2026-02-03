<script lang="ts">
    import '../app.css';
    import * as Sidebar from '$lib/components/ui/sidebar';
    import {
        House,
        Tag,
        ArrowLeftRight,
        Upload,
        Settings,
        SunIcon,
        MoonIcon,
    } from '@lucide/svelte';
    import { page } from '$app/state';
    import { Button } from '$lib/components/ui/button';
    import { toggleMode, ModeWatcher } from 'mode-watcher';
    import { Wallet } from '@lucide/svelte';
    import * as m from '$lib/paraglide/messages';
    import { getLocale, localizeHref, deLocalizeHref } from '$lib/paraglide/runtime';

    let { children } = $props();

    $effect(() => {
        document.documentElement.lang = getLocale();
    });

    const navItems = $derived([
        { href: localizeHref('/'), label: m.nav_home(), icon: House },
        { href: localizeHref('/categories'), label: m.nav_categories(), icon: Tag },
        { href: localizeHref('/transactions'), label: m.nav_transactions(), icon: ArrowLeftRight },
        { href: localizeHref('/import'), label: m.nav_import(), icon: Upload },
        { href: localizeHref('/admin'), label: m.nav_admin(), icon: Settings },
    ]);

    const isActive = (href: string) => {
        const currentPath = deLocalizeHref(page.url.pathname);
        const itemPath = deLocalizeHref(href);
        return currentPath === itemPath;
    };
</script>

<ModeWatcher />
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
                    <span class="sr-only">Toggle theme</span>
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
