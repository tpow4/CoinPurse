using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services
{
    public interface IBalanceService
    {
        Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync();
        Task<IEnumerable<AccountBalanceDto>> GetBalancesByAccountIdAsync(int accountId);
        Task<AccountBalanceDto> CreateBalanceAsync(CreateAccountBalanceDto balanceDto);
    }
}
