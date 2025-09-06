using CoinPurseApi.Dtos;
using CoinPurseApi.Models;

namespace CoinPurseApi.Services
{
    public interface IPeriodService
    {
        Task<Period> GetCurrentWeekPeriodAsync();
        Task<Period> GetOrCreateCurrentWeekPeriodAsync();
        Task<Period> GetPeriodForDateAsync(DateTime date);
        Task<Period> GetOrCreatePeriodForDateAsync(DateTime date);
        Task<IEnumerable<Period>> GetRecentPeriodsAsync(int count = 12);
        Task<bool> HasBalancesForCurrentWeekAsync();
        Task<IEnumerable<AccountBalance>> GetBalancesForPeriodAsync(int periodId);
    }
}
