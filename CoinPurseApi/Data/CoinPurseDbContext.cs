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
        private const int NUMBER_MONTHS_SEEDED_DATA = 5;

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder
            .UseSqlite(_configuration.GetConnectionString("DefaultConnection"))
            //Requires both UseSeeding and UseAsyncSeeding per MS docs
            //https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#configuration-options-useseeding-and-useasyncseeding-methods
            .UseSeeding((context, _) =>
            {
                if(!context.Set<Period>().Any())
                {
                    var fiscalPeriods = GetSeedingPeriods(NUMBER_MONTHS_SEEDED_DATA);
                    context.Set<Period>().AddRange(fiscalPeriods);
                    context.SaveChanges();
                }
            })
            .UseAsyncSeeding(async (context, _, cancellationToken) =>
            {
                if (!context.Set<Period>().Any())
                {
                    var fiscalPeriods = GetSeedingPeriods(NUMBER_MONTHS_SEEDED_DATA);
                    await context.Set<Period>().AddRangeAsync(fiscalPeriods, cancellationToken);
                    await context.SaveChangesAsync(cancellationToken);
                }
            });

        private static List<Period> GetSeedingPeriods(int numberMonths)
        {
            var now = DateTime.UtcNow;
            var startingDate = now.AddMonths(-numberMonths + 1);
            var fiscalPeriods = new List<Period>();

            var currentPeriodId = 1;
            var selectedMonth = startingDate.Month;
            var selectedYear = startingDate.Year;

            for (var i = 0; i < numberMonths; i++)
            {
                var daysInMonth = DateTime.DaysInMonth(selectedYear, selectedMonth);
                fiscalPeriods.Add(new Period
                {
                    Id = currentPeriodId,
                    Name = $"periods.name.{currentPeriodId}",
                    StartDate = new DateTime(selectedYear, selectedMonth, 1, 0, 0, 0, DateTimeKind.Utc),
                    EndDate = new DateTime(selectedYear, selectedMonth, daysInMonth, 23, 59, 59, DateTimeKind.Utc)
                });

                if (selectedMonth == 12)
                {
                    selectedMonth = 1;
                    selectedYear++;
                }
                else
                {
                    selectedMonth++;
                }

                currentPeriodId++;
            }

            return fiscalPeriods;
        }

    }
}
