using CoinPurseApi.Models;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Data
{
    public class CoinPurseDbContext(IConfiguration configuration) : DbContext
    {
        public DbSet<Account> Accounts { get; set; }
        public DbSet<Institution> Institutions { get; set; }
        public DbSet<Period> Periods { get; set; }
        public DbSet<AccountBalance> AccountBalances { get; set; }

        private readonly IConfiguration _configuration = configuration;

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder
            .UseSqlite(_configuration.GetConnectionString("DefaultConnection"));
    }
}
