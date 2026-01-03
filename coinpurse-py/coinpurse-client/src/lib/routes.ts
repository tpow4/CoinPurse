/**
 * Route definitions for svelte-spa-router
 */

import Dashboard from '../pages/dashboard.svelte';
import Categories from '../pages/categories.svelte';
import Transactions from '../pages/transactions.svelte';
import Admin from '../pages/admin.svelte';
import NotFound from '../pages/not-found.svelte';

export const routes = {
  '/': Dashboard,
  '/categories': Categories,
  '/transactions': Transactions,
  '/admin': Admin,
  '*': NotFound,
};
