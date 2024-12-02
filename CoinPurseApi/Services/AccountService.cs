using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class AccountService : IAccountService
    {
        private readonly CoinPurseDbContext _context;
        private readonly ILogger<AccountService> _logger;

        public AccountService(
            CoinPurseDbContext context,
            ILogger<AccountService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<AccountDto> GetAccountAsync(int id)
        {
            var account = await _context.Accounts
                .Include(a => a.Institution)
                .Include(a => a.Balances)
                .FirstOrDefaultAsync(a => a.Id == id);

            return account?.ToDto();
        }

        public async Task<IEnumerable<AccountDto>> GetAccountsAsync()
        {
            var accounts = await _context.Accounts
                .Include(a => a.Institution)
                .Include(a => a.Balances)
                .ToListAsync();

            return accounts.Select(a => a.ToDto());
        }

        public async Task<AccountDto> CreateAccountAsync(CreateAccountDto accountDto)
        {
            var account = accountDto.ToEntity();

            try
            {
                _context.Accounts.Add(account);
                await _context.SaveChangesAsync();

                // Reload the account with relations
                account = await _context.Accounts
                    .Include(a => a.Institution)
                    .Include(a => a.Balances)
                    .FirstAsync(a => a.Id == account.Id);

                return account.ToDto();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating account");
                throw;
            }
        }

        public async Task<AccountDto> UpdateAccountAsync(int id, UpdateAccountDto accountDto)
        {
            var account = await _context.Accounts
                .Include(a => a.Institution)
                .Include(a => a.Balances)
                .FirstOrDefaultAsync(a => a.Id == id);

            if (account == null)
            {
                throw new KeyNotFoundException($"Account with ID {id} not found");
            }

            accountDto.UpdateEntity(account);

            try
            {
                await _context.SaveChangesAsync();
                return account.ToDto();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating account {AccountId}", id);
                throw;
            }
        }

        public async Task<bool> DeleteAccountAsync(int id)
        {
            var account = await _context.Accounts.FindAsync(id);
            if (account == null)
            {
                return false;
            }

            _context.Accounts.Remove(account);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<IEnumerable<BalanceDto>> GetAccountBalancesAsync(int accountId)
        {
            var balances = await _context.Balances
                .Include(b => b.Account)
                .Where(b => b.AccountId == accountId)
                .OrderByDescending(b => b.Timestamp)
                .ToListAsync();

            return balances.Select(b => b.ToDto());
        }
    }

}
