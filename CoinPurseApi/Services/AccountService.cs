using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class AccountService(
        CoinPurseDbContext context,
        ILogger<AccountService> logger) : IAccountService
    {
        public async Task<AccountDto> GetAccountAsync(int id)
        {
            var account = await context.Accounts
                .Include(a => a.Institution)
                .Include(a => a.AccountPeriods)
                .SingleAsync(a => a.Id == id);

            return account?.ToDto();
        }

        public async Task<IEnumerable<AccountDto>> GetAccountsAsync()
        {
            var accounts = await context.Accounts
                .Include(a => a.Institution)
                .Include(a => a.AccountPeriods)
                .ToListAsync();

            return accounts.Select(a => a.ToDto());
        }

        public async Task<AccountDto> CreateAccountAsync(CreateAccountDto accountDto)
        {
            var account = accountDto.ToEntity();
            account.IsActive = true;

            try
            {
                context.Accounts.Add(account);
                await context.SaveChangesAsync();

                // Reload the account with relations
                account = await context.Accounts
                    .Include(a => a.Institution)
                    .Include(a => a.AccountPeriods)
                    .SingleAsync(a => a.Id == account.Id);

                return account.ToDto();
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating account");
                throw;
            }
        }

        public async Task<AccountDto> UpdateAccountAsync(int id, UpdateAccountDto accountDto)
        {
            var account = await context.Accounts
                .Include(a => a.Institution)
                .Include(a => a.AccountPeriods)
                .SingleOrDefaultAsync(a => a.Id == id);

            if (account == null)
            {
                throw new KeyNotFoundException($"Account with ID {id} not found");
            }

            accountDto.UpdateEntity(account);

            try
            {
                await context.SaveChangesAsync();
                return account.ToDto();
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error updating account {AccountId}", id);
                throw;
            }
        }

        public async Task<bool> DeleteAccountAsync(int id)
        {
            var account = await context.Accounts.FindAsync(id);
            if (account == null)
            {
                return false;
            }

            context.Accounts.Remove(account);
            await context.SaveChangesAsync();
            return true;
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetAccountBalancesAsync(int accountId)
        {
            var balances = await context.AccountBalances
                .Include(b => b.Account)
                .Where(b => b.AccountId == accountId)
                .OrderByDescending(b => b.PeriodId)
                .ToListAsync();

            return balances.Select(b => b.ToDto());
        }
    }

}
