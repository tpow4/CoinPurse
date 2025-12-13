<script lang="ts">
  import * as Sidebar from "$lib/components/ui/sidebar";
  import { House, Building, Tag, Wallet, ArrowLeftRight, Settings } from "@lucide/svelte";
  import { location } from "svelte-spa-router";

  const navItems = [
    { href: "#/", label: "Home", icon: House, path: "/" },
    {
      href: "#/institutions",
      label: "Institutions",
      icon: Building,
      path: "/institutions",
    },
    {
      href: "#/categories",
      label: "Categories",
      icon: Tag,
      path: "/categories",
    },
    { href: "#/accounts", label: "Accounts", icon: Wallet, path: "/accounts" },
    {
      href: "#/transactions",
      label: "Transactions",
      icon: ArrowLeftRight,
      path: "/transactions",
    },
    {
      href: "#/admin",
      label: "Admin",
      icon: Settings,
      path: "/admin",
    },
  ];
</script>

<Sidebar.Provider>
  <Sidebar.Sidebar>
    <Sidebar.SidebarHeader>
      <div class="flex items-center gap-2 px-2 py-4">
        <Wallet class="size-6" />
        <h2 class="text-xl font-bold">CoinPurse</h2>
      </div>
    </Sidebar.SidebarHeader>

    <Sidebar.SidebarContent>
      <div class="px-4 py-2">
        <Sidebar.SidebarMenu>
          {#each navItems as item}
            <Sidebar.SidebarMenuItem>
              <Sidebar.SidebarMenuButton
                isActive={$location === item.path}
                tooltipContent={item.label}
              >
                {#snippet child({ props })}
                  <a href={item.href} {...props}>
                    <svelte:component this={item.icon} />
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
      <slot />
    </main>
  </Sidebar.SidebarInset>
</Sidebar.Provider>
