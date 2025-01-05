using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class BalanceService : IBalanceService
    {
        private readonly CoinPurseDbContext _context;
        private readonly ILogger<BalanceService> _logger;

        public BalanceService(
            CoinPurseDbContext context,
            ILogger<BalanceService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<AccountBalanceDto> CreateBalanceAsync(CreateAccountBalanceDto balanceDto)
        {
            var accountBalance = balanceDto.ToEntity();

            try
            {
                _context.AccountBalances.Add(accountBalance);
                await _context.SaveChangesAsync();

                // Reload with account information
                accountBalance = await _context.AccountBalances
                    .SingleAsync(ap => ap.AccountId == accountBalance.AccountId &&
                                   ap.PeriodId == accountBalance.PeriodId);

                return accountBalance.ToDto();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating balance");
                throw;
            }
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetBalancesByAccountIdAsync(int accountId)
        {
            var accountBalances = await _context.AccountBalances
                .Include(balance => balance.Account)
                .Where(balance => balance.AccountId == accountId && balance.Account.IsActive)
                .ToListAsync();

            return accountBalances.Select(ap => ap.ToDto());
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync()
        {
            var accountBalances = await _context.AccountBalances
                .Include(balance => balance.Account)
                .Where(balance => balance.Account.IsActive)
                .ToListAsync();

            return accountBalances.Select(ap => ap.ToDto());
        }
    }
}
