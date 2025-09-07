using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services.Interfaces
{
    public interface IBalanceService
    {
        Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync();
        Task<IEnumerable<AccountBalanceDto>> GetBalancesByAccountIdAsync(int accountId);
        Task<IEnumerable<AccountBalanceDto>> CreateBalancesForMonthAsync(CreateBalancesForMonthDto dto);
        Task<IEnumerable<AccountBalanceDto>> CreateBalancesForDateAsync(CreateBalancesForDateDto dto);

    }
}
