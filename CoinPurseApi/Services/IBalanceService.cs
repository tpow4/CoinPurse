using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services
{
    public interface IBalanceService
    {
        Task<BalanceDto> CreateBalanceAsync(CreateBalanceDto balanceDto);
        Task<IEnumerable<BalanceDto>> GetBalancesForPeriodAsync(int accountId, DateTime startDate, DateTime endDate);
    }
}
