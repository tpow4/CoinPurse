<script lang="ts">
  import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
  } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
</script>

<div class="container mx-auto p-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold mb-2">CoinPurse</h1>
    <p class="text-muted-foreground text-lg">Personal Finance Tracking</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <Card>
      <CardHeader>
        <CardTitle>Institutions</CardTitle>
        <CardDescription>Manage your financial institutions</CardDescription>
      </CardHeader>
      <CardContent>
        <Button href="#/institutions" class="w-full">View Institutions</Button>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Categories</CardTitle>
        <CardDescription>Organize transaction categories</CardDescription>
      </CardHeader>
      <CardContent>
        <Button href="#/categories" class="w-full">View Categories</Button>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Accounts</CardTitle>
        <CardDescription>Track your accounts</CardDescription>
      </CardHeader>
      <CardContent>
        <Button href="#/accounts" class="w-full">View Accounts</Button>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Transactions</CardTitle>
        <CardDescription>View and manage transactions</CardDescription>
      </CardHeader>
      <CardContent>
        <Button href="#/transactions" class="w-full">View Transactions</Button>
      </CardContent>
    </Card>
  </div>
</div>
