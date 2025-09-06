using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using CoinPurseApi.Services.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class BalanceService(
        CoinPurseDbContext context,
        ILogger<BalanceService> logger) : IBalanceService
    {
        public async Task<AccountBalanceDto> CreateBalanceAsync(CreateAccountBalanceDto balanceDto)
        {
            var accountBalance = balanceDto.ToEntity();

            try
            {
                context.AccountBalances.Add(accountBalance);
                await context.SaveChangesAsync();

                // Reload with account information
                accountBalance = await context.AccountBalances
                    .SingleAsync(ap => ap.AccountId == accountBalance.AccountId &&
                                   ap.PeriodId == accountBalance.PeriodId);

                return accountBalance.ToDto();
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating balance");
                throw;
            }
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetBalancesByAccountIdAsync(int accountId)
        {
            var accountBalances = await context.AccountBalances
                .Include(balance => balance.Account)
                .Where(balance => balance.AccountId == accountId && balance.Account.IsActive)
                .ToListAsync();

            return accountBalances.Select(ap => ap.ToDto());
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync()
        {
            var accountBalances = await context.AccountBalances
                .Include(balance => balance.Account)
                .Where(balance => balance.Account.IsActive)
                .ToListAsync();

            return accountBalances.Select(ap => ap.ToDto());
        }

        public async Task<IEnumerable<AccountDto>> GetAccountsMissingBalanceForPeriod(int periodId)
        {
            var accountsWithBalance = await context.AccountBalances
                .Where(ab => ab.PeriodId == periodId)
                .Select(ab => ab.AccountId)
                .ToListAsync();

            var allActiveAccounts = await context.Accounts
                .Include(a => a.Institution)
                .Where(a => a.IsActive)
                .Where(a => !accountsWithBalance.Contains(a.Id))
                .ToListAsync();

            return allActiveAccounts.Select(a => a.ToDto());
        }
    }
}
