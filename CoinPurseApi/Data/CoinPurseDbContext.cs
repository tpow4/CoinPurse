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
        private const int NUMBER_YEARS_SEEDED_DATA = 2; // Reduced for weekly periods

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder
            .UseSqlite(_configuration.GetConnectionString("DefaultConnection"))
            //Requires both UseSeeding and UseAsyncSeeding per MS docs
            //https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#configuration-options-useseeding-and-useasyncseeding-methods
            .UseSeeding((context, _) =>
            {
                if (!context.Set<Period>().Any())
                {
                    var weeklyPeriods = GetWeeklyPeriods(NUMBER_YEARS_SEEDED_DATA);
                    context.Set<Period>().AddRange(weeklyPeriods);
                    context.SaveChanges();
                }
            })
            .UseAsyncSeeding(async (context, _, cancellationToken) =>
            {
                if (!context.Set<Period>().Any())
                {
                    var weeklyPeriods = GetWeeklyPeriods(NUMBER_YEARS_SEEDED_DATA);
                    await context.Set<Period>().AddRangeAsync(weeklyPeriods, cancellationToken);
                    await context.SaveChangesAsync(cancellationToken);
                }
            });

        private static List<Period> GetWeeklyPeriods(int numberYears)
        {
            var periods = new List<Period>();
            var periodId = 1;

            // Start from beginning of current year
            var currentYear = DateTime.Now.Year;
            var yearStart = new DateTime(currentYear, 1, 1, 0, 0, 0, DateTimeKind.Utc);

            // Find the first Monday of the year (or start from Jan 1 if it's Monday)
            var firstMonday = yearStart.GetStartOfWeek();

            // Generate weeks for the specified number of years
            var totalWeeks = 52 * numberYears + 4; // Extra weeks to handle year boundaries

            for (var weekIndex = 0; weekIndex < totalWeeks; weekIndex++)
            {
                var weekStart = firstMonday.AddDays(weekIndex * 7);
                var weekEnd = weekStart.AddDays(6).AddHours(23).AddMinutes(59).AddSeconds(59);

                periods.Add(new Period
                {
                    Id = periodId,
                    Name = $"Week of {weekStart:MMM dd, yyyy}",
                    StartDate = weekStart,
                    EndDate = weekEnd
                });

                periodId++;
            }

            return periods;
        }
    }
}

// Extension method to get start of week (Monday)
public static class DateTimeExtensions
{
    public static DateTime GetStartOfWeek(this DateTime dateTime)
    {
        var diff = (7 + (dateTime.DayOfWeek - DayOfWeek.Monday)) % 7;
        return dateTime.AddDays(-1 * diff).Date;
    }

    public static DateTime GetEndOfWeek(this DateTime dateTime)
    {
        return dateTime.GetStartOfWeek().AddDays(6).AddHours(23).AddMinutes(59).AddSeconds(59);
    }
}