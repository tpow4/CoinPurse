using CoinPurseApi.Data;
using CoinPurseApi.Models;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class PeriodService(CoinPurseDbContext context, ILogger<PeriodService> logger) : IPeriodService
    {

        /// <summary>
        /// Gets the period for the current week. Returns null if it doesn't exist.
        /// </summary>
        public async Task<Period> GetCurrentWeekPeriodAsync()
        {
            var weekStart = DateTime.Now.GetStartOfWeek();
            return await GetPeriodForDateAsync(weekStart);
        }

        /// <summary>
        /// Gets or creates the period for the current week.
        /// </summary>
        public async Task<Period> GetOrCreateCurrentWeekPeriodAsync()
        {
            var weekStart = DateTime.Now.GetStartOfWeek();
            return await GetOrCreatePeriodForDateAsync(weekStart);
        }

        /// <summary>
        /// Gets the period that contains the specified date.
        /// </summary>
        public async Task<Period> GetPeriodForDateAsync(DateTime date)
        {
            var dateOnly = date.Date;
            return await context.Periods
                .FirstOrDefaultAsync(p => p.StartDate.Date <= dateOnly && p.EndDate.Date >= dateOnly);
        }

        /// <summary>
        /// Gets or creates the period that should contain the specified date.
        /// </summary>
        public async Task<Period> GetOrCreatePeriodForDateAsync(DateTime date)
        {
            var existingPeriod = await GetPeriodForDateAsync(date);
            if (existingPeriod != null)
            {
                return existingPeriod;
            }

            // Create new period for this week
            var weekStart = date.GetStartOfWeek();
            var weekEnd = weekStart.GetEndOfWeek();

            // Get the next available ID
            var maxId = await context.Periods.MaxAsync(p => (int?)p.Id) ?? 0;

            var newPeriod = new Period
            {
                Id = maxId + 1,
                Name = $"Week of {weekStart:MMM dd, yyyy}",
                StartDate = weekStart,
                EndDate = weekEnd
            };

            try
            {
                context.Periods.Add(newPeriod);
                await context.SaveChangesAsync();

                logger.LogInformation("Created new period: {PeriodName} ({StartDate} - {EndDate})",
                    newPeriod.Name, newPeriod.StartDate, newPeriod.EndDate);

                return newPeriod;
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating period for date {Date}", date);
                throw new InvalidOperationException("An error occurred while creating the period", ex);
            }
        }

        /// <summary>
        /// Gets the most recent periods, ordered by start date descending.
        /// </summary>
        public async Task<IEnumerable<Period>> GetRecentPeriodsAsync(int count = 12)
        {
            return await context.Periods
                .OrderByDescending(p => p.StartDate)
                .Take(count)
                .ToListAsync();
        }

        /// <summary>
        /// Checks if any account balances have been entered for the current week.
        /// </summary>
        public async Task<bool> HasBalancesForCurrentWeekAsync()
        {
            var currentPeriod = await GetCurrentWeekPeriodAsync();
            if (currentPeriod == null)
            {
                return false;
            }

            return await context.AccountBalances
                .AnyAsync(ab => ab.PeriodId == currentPeriod.Id);
        }

        /// <summary>
        /// Gets all account balances for a specific period.
        /// </summary>
        public async Task<IEnumerable<AccountBalance>> GetBalancesForPeriodAsync(int periodId)
        {
            return await context.AccountBalances
                .Include(ab => ab.Account)
                .Where(ab => ab.PeriodId == periodId)
                .ToListAsync();
        }
    }
}
