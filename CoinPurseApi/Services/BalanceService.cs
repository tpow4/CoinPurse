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

        public async Task<BalanceDto> CreateBalanceAsync(CreateBalanceDto balanceDto)
        {
            var balance = balanceDto.ToEntity();

            try
            {
                _context.Balances.Add(balance);
                await _context.SaveChangesAsync();

                // Reload with account information
                balance = await _context.Balances
                    .Include(b => b.Account)
                    .FirstAsync(b => b.AccountId == balance.AccountId &&
                                   b.Timestamp == balance.Timestamp);

                return balance.ToDto();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating balance");
                throw;
            }
        }

        public async Task<IEnumerable<BalanceDto>> GetBalancesForPeriodAsync(
            int accountId,
            DateTime startDate,
            DateTime endDate)
        {
            var balances = await _context.Balances
                .Include(b => b.Account)
                .Where(b => b.AccountId == accountId &&
                           b.Timestamp >= startDate &&
                           b.Timestamp <= endDate)
                .OrderByDescending(b => b.Timestamp)
                .ToListAsync();

            return balances.Select(b => b.ToDto());
        }
    }
}
