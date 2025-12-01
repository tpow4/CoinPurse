<script lang="ts">
</script>

<div class="home">
  <h1>CoinPurse</h1>
  <p>Personal Finance Tracking</p>

  <div class="welcome-cards">
    <div class="card">
      <h2>Institutions</h2>
      <p>Manage your financial institutions</p>
      <a href="#/institutions">View Institutions</a>
    </div>

    <div class="card">
      <h2>Categories</h2>
      <p>Organize transaction categories</p>
      <a href="#/categories">View Categories</a>
    </div>

    <div class="card">
      <h2>Accounts</h2>
      <p>Track your accounts</p>
      <a href="#/accounts">View Accounts</a>
    </div>

    <div class="card">
      <h2>Transactions</h2>
      <p>View and manage transactions</p>
      <a href="#/transactions">View Transactions</a>
    </div>
  </div>
</div>

<style>
  .home {
    padding: 2rem;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
  }

  .welcome-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
  }

  .card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1.5rem;
    background: #fff;
  }

  .card h2 {
    margin-top: 0;
    font-size: 1.5rem;
  }

  .card p {
    color: #666;
    margin: 0.5rem 0 1rem;
  }

  .card a {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #646cff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
  }

  .card a:hover {
    background: #535bf2;
  }
</style>
