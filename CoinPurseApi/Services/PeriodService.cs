using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class PeriodService(CoinPurseDbContext context, ILogger<AccountService> logger) : IPeriodService
    {
        public async Task<IEnumerable<PeriodDto>> GetPeriods()
        {
            var periods = await context.Periods
                .Select(p => new PeriodDto
                {
                    Id = p.Id,
                    Name = p.Name,
                    StartDate = p.StartDate,
                    EndDate = p.EndDate
                })
                .OrderBy(p => p.Id)
                .ToListAsync();
            return periods;
        }
    }
}
