using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using CoinPurseApi.Models;
using CoinPurseApi.Services.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class PeriodService(CoinPurseDbContext context) : IPeriodService
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
                .OrderBy(p => p.StartDate)
                .ToListAsync();
            return periods;
        }

        public async Task<PeriodDto> CreatePeriod(CreatePeriodDto createPeriodDto)
        {
            var period = new Period
            {
                Name = createPeriodDto.Name,
                StartDate = createPeriodDto.StartDate,
                EndDate = createPeriodDto.EndDate
            };

            context.Periods.Add(period);
            await context.SaveChangesAsync();

            return new PeriodDto
            {
                Id = period.Id,
                Name = period.Name,
                StartDate = period.StartDate,
                EndDate = period.EndDate
            };
        }

        public async Task<PeriodDto> GetOrCreatePeriodForMonth(int year, int month)
        {
            // First, try to find existing period for this month
            var existingPeriod = await GetPeriodForDate(new DateTime(year, month, 1)); //TODO check DateTimeKind?
            if (existingPeriod != null)
            {
                return existingPeriod;
            }

            // Create new period for this month
            var startDate = new DateTime(year, month, 1, 0, 0, 0, DateTimeKind.Utc);
            var endDate = new DateTime(year, month, DateTime.DaysInMonth(year, month), 23, 59, 59, DateTimeKind.Utc);

            var createDto = new CreatePeriodDto
            {
                Name = $"{year}-{month:D2}",
                StartDate = startDate,
                EndDate = endDate
            };

            return await CreatePeriod(createDto);
        }

        public async Task<PeriodDto?> GetPeriodForDate(DateTime date)
        {
            var period = await context.Periods
                .Where(p => date >= p.StartDate && date <= p.EndDate)
                .Select(p => new PeriodDto
                {
                    Id = p.Id,
                    Name = p.Name,
                    StartDate = p.StartDate,
                    EndDate = p.EndDate
                })
                .FirstOrDefaultAsync();

            return period;
        }
    }
}