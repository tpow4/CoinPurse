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
                    .Include(ap => ap.Account)
                    .OrderByDescending(ap => ap.PeriodId)
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

        public async Task<IEnumerable<AccountBalanceDto>> GetBalancesForRangeAsync(
            int accountId,
            int startPeriodId,
            int endPeriodId)
        {
            var accountBalances = await _context.AccountBalances
                .Include(ap => ap.Account)
                .Where(ap => ap.AccountId == accountId &&
                           ap.PeriodId >= startPeriodId &&
                           ap.PeriodId <= endPeriodId)
                .OrderByDescending(b => b.PeriodId)
                .ToListAsync();

            return accountBalances.Select(ap => ap.ToDto());
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync()
        {
            var accountBalances = await _context.AccountBalances
                .Include(ap => ap.Account)
                .OrderByDescending(b => b.PeriodId)
                .ToListAsync();

            return accountBalances.Select(ap => ap.ToDto());
        }
    }
}
