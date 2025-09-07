using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using CoinPurseApi.Models;
using CoinPurseApi.Services.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class BalanceService(CoinPurseDbContext context, IPeriodService periodService) : IBalanceService
    {
        public async Task<IEnumerable<AccountBalanceDto>> GetAllBalancesAsync()
        {
            var balances = await context.AccountBalances
                .Select(ab => new AccountBalanceDto
                {
                    PeriodId = ab.PeriodId,
                    AccountId = ab.AccountId,
                    Amount = ab.Amount
                })
                .ToListAsync();

            return balances;
        }

        public async Task<IEnumerable<AccountBalanceDto>> GetBalancesByAccountIdAsync(int accountId)
        {
            var balances = await context.AccountBalances
                .Where(ab => ab.AccountId == accountId)
                .Select(ab => new AccountBalanceDto
                {
                    PeriodId = ab.PeriodId,
                    AccountId = ab.AccountId,
                    Amount = ab.Amount
                })
                .ToListAsync();

            return balances;
        }

        public async Task<IEnumerable<AccountBalanceDto>> CreateBalancesForMonthAsync(CreateBalancesForMonthDto dto)
        {
            // Ensure period exists for the specified month
            var period = await periodService.GetOrCreatePeriodForMonth(dto.Year, dto.Month);

            // Create or update balances
            return await CreateOrUpdateBalancesForPeriod(dto.Balances, period.Id);
        }

        public async Task<IEnumerable<AccountBalanceDto>> CreateBalancesForDateAsync(CreateBalancesForDateDto dto)
        {
            var year = dto.TargetDate.Year;
            var month = dto.TargetDate.Month;

            // Ensure period exists for the month of the target date
            var period = await periodService.GetOrCreatePeriodForMonth(year, month);

            // Create or update balances
            return await CreateOrUpdateBalancesForPeriod(dto.Balances, period.Id);
        }

        private async Task<IEnumerable<AccountBalanceDto>> CreateOrUpdateBalancesForPeriod(
            List<CreateAccountBalanceDto> balancesDto,
            int periodId)
        {
            var results = new List<AccountBalanceDto>();

            foreach (var balanceDto in balancesDto)
            {
                // Check if balance already exists for this account and period
                var existingBalance = await context.AccountBalances
                    .FirstOrDefaultAsync(ab => ab.AccountId == balanceDto.AccountId && ab.PeriodId == periodId);

                if (existingBalance != null)
                {
                    // Update existing balance
                    existingBalance.Amount = balanceDto.Amount;
                    existingBalance.CreatedAt = DateTime.UtcNow;
                }
                else
                {
                    // Create new balance
                    var balance = new AccountBalance
                    {
                        AccountId = balanceDto.AccountId,
                        PeriodId = periodId,
                        Amount = balanceDto.Amount,
                        CreatedAt = DateTime.UtcNow
                    };
                    context.AccountBalances.Add(balance);
                }

                results.Add(new AccountBalanceDto
                {
                    AccountId = balanceDto.AccountId,
                    PeriodId = periodId,
                    Amount = balanceDto.Amount
                });
            }

            await context.SaveChangesAsync();
            return results;
        }
    }
}