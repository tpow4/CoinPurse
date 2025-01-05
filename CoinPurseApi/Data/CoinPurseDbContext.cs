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
        private const int NUMBER_YEARS_SEEDED_DATA = 5;

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder
            .UseSqlite(_configuration.GetConnectionString("DefaultConnection"))
            //Requires both UseSeeding and UseAsyncSeeding per MS docs
            //https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#configuration-options-useseeding-and-useasyncseeding-methods
            .UseSeeding((context, _) =>
            {
                if(!context.Set<Period>().Any())
                {
                    var fiscalPeriods = GetSeedingPeriods(NUMBER_YEARS_SEEDED_DATA);
                    context.Set<Period>().AddRange(fiscalPeriods);
                    context.SaveChanges();
                }
            })
            .UseAsyncSeeding(async (context, _, cancellationToken) =>
            {
                if (!context.Set<Period>().Any())
                {
                    var fiscalPeriods = GetSeedingPeriods(NUMBER_YEARS_SEEDED_DATA);
                    await context.Set<Period>().AddRangeAsync(fiscalPeriods, cancellationToken);
                    await context.SaveChangesAsync(cancellationToken);
                }
            });

        private static List<Period> GetSeedingPeriods(int numberYears)
        {
            var currentYear = DateTime.Now.Year;
            var currentPeriodId = 1;
            var fiscalPeriods = new List<Period>();
            for (var yearIndex = 0; yearIndex < numberYears; yearIndex++)
            {
                var selectedYear = currentYear + yearIndex;
                for (var monthIndex = 1; monthIndex <= 12; monthIndex++)
                {
                    fiscalPeriods.AddRange([
                        new Period
                            {
                                Id = currentPeriodId,
                                Name = $"periods.name.{currentPeriodId}",
                                StartDate = new DateTime(currentYear + yearIndex, monthIndex, 1, 0, 0, 0, DateTimeKind.Utc),
                                EndDate = new DateTime(currentYear + yearIndex, monthIndex, DateTime.DaysInMonth(selectedYear, monthIndex), 23, 59, 59, DateTimeKind.Utc)
                            }
                    ]);
                    currentPeriodId++;
                }
            }

            return fiscalPeriods;
        }
    }
}
