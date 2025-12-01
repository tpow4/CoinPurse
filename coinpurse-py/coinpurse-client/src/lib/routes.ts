/**
 * Route definitions for svelte-spa-router
 */

import Home from '../pages/Home.svelte';
import Institutions from '../pages/Institutions.svelte';
import Categories from '../pages/Categories.svelte';
import Accounts from '../pages/Accounts.svelte';
import Transactions from '../pages/Transactions.svelte';
import NotFound from '../pages/NotFound.svelte';

export const routes = {
  '/': Home,
  '/institutions': Institutions,
  '/categories': Categories,
  '/accounts': Accounts,
  '/transactions': Transactions,
  '*': NotFound,
};
