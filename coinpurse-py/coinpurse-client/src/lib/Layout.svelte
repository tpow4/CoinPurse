<script lang="ts">
  // Reactive statement to check active route
  $: currentPath = $location;

  function isActive(path: string): boolean {
    return currentPath === path;
  }
</script>

<div class="layout">
  <nav class="sidebar">
    <div class="logo">
      <h2>CoinPurse</h2>
    </div>
    <ul class="nav-links">
      <li>
        <a href="#/" class:active={isActive("/")}> Home </a>
      </li>
      <li>
        <a href="#/institutions" class:active={isActive("/institutions")}>
          Institutions
        </a>
      </li>
      <li>
        <a href="#/categories" class:active={isActive("/categories")}>
          Categories
        </a>
      </li>
      <li>
        <a href="#/accounts" class:active={isActive("/accounts")}> Accounts </a>
      </li>
      <li>
        <a href="#/transactions" class:active={isActive("/transactions")}>
          Transactions
        </a>
      </li>
    </ul>
  </nav>

  <main class="content">
    <slot />
  </main>
</div>

<style>
  .layout {
    display: flex;
    min-height: 100vh;
  }

  .sidebar {
    width: 250px;
    background: #2c3e50;
    color: white;
    padding: 1rem;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  }

  .logo {
    padding: 1rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 1rem;
  }

  .logo h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #3498db;
  }

  .nav-links {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .nav-links li {
    margin: 0.5rem 0;
  }

  .nav-links a {
    display: block;
    padding: 0.75rem 1rem;
    color: #ecf0f1;
    text-decoration: none;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .nav-links a:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .nav-links a.active {
    background: #3498db;
    color: white;
  }

  .content {
    flex: 1;
    background: #ecf0f1;
    overflow-y: auto;
  }
</style>
