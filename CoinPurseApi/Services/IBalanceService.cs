using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services
{
    public interface IBalanceService
    {
        Task<BalanceDto> CreateBalanceAsync(CreateBalanceDto balanceDto);
        Task<IEnumerable<BalanceDto>> GetBalancesForRangeAsync(int accountId, int startPeriodId, int endPeriodId);
    }
}
