/**
 * Route definitions for svelte-spa-router
 */

import Home from '../pages/home.svelte';
import Institutions from '../pages/institutions.svelte';
import Categories from '../pages/categories.svelte';
import Accounts from '../pages/accounts.svelte';
import Transactions from '../pages/transactions.svelte';
import Admin from '../pages/admin.svelte';
import NotFound from '../pages/not-found.svelte';

export const routes = {
  '/': Home,
  '/institutions': Institutions,
  '/categories': Categories,
  '/accounts': Accounts,
  '/transactions': Transactions,
  '/admin': Admin,
  '*': NotFound,
};
