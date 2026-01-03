<script lang="ts">
  import './app.css';
  import Router from 'svelte-spa-router';
  import { ModeWatcher } from 'mode-watcher';
  import Layout from './lib/layout.svelte';
  import { routes } from './lib/routes';
</script>

<ModeWatcher />
<Layout>
  <Router {routes} />
</Layout>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }

  :global(*) {
    box-sizing: border-box;
  }
</style>
