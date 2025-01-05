using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services
{
    public interface IAccountService
    {
        Task<AccountDto> GetAccountAsync(int id);
        Task<IEnumerable<AccountDto>> GetAccountsAsync();
        Task<AccountDto> CreateAccountAsync(CreateAccountDto accountDto);
        Task<AccountDto> UpdateAccountAsync(int id, UpdateAccountDto accountDto);
        Task<bool> DeleteAccountAsync(int id);
        Task<IEnumerable<AccountBalanceDto>> GetAccountBalancesAsync(int accountId);
    }
}
