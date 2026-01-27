<script lang="ts">
    import '../app.css';
    import * as Sidebar from '$lib/components/ui/sidebar';
    import {
        House,
        Tag,
        Wallet,
        ArrowLeftRight,
        Upload,
        Settings,
        SunIcon,
        MoonIcon,
    } from '@lucide/svelte';
    import { page } from '$app/state';
    import { Button } from '$lib/components/ui/button';
    import { toggleMode, ModeWatcher } from 'mode-watcher';

    let { children } = $props();

    const navItems = [
        { href: '/', label: 'Home', icon: House },
        { href: '/categories', label: 'Categories', icon: Tag },
        { href: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
        { href: '/import', label: 'Import', icon: Upload },
        { href: '/admin', label: 'Admin', icon: Settings },
    ];

    const isActive = (href: string) => page.url.pathname === href;
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
