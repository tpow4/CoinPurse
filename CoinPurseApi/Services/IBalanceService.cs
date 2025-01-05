using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services
{
    public interface IBalanceService
    {
        Task<AccountBalanceDto> CreateBalanceAsync(CreateAccountBalanceDto balanceDto);
        Task<IEnumerable<AccountBalanceDto>> GetBalancesForRangeAsync(int accountId, int startPeriodId, int endPeriodId);
        Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync();
    }
}
