using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services.Interfaces
{
    public interface IBalanceService
    {
        Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync();
        Task<IEnumerable<AccountBalanceDto>> GetBalancesByAccountIdAsync(int accountId);
        Task<AccountBalanceDto> CreateBalanceAsync(CreateAccountBalanceDto balanceDto);

        Task<IEnumerable<AccountDto>> GetAccountsMissingBalanceForPeriod(int periodId);
    }
}
