using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services.Interfaces
{
    public interface IPeriodService
    {
        Task<IEnumerable<PeriodDto>> GetPeriods();
        Task<PeriodDto> CreatePeriod(CreatePeriodDto createPeriodDto);
        Task<PeriodDto> GetOrCreatePeriodForMonth(int year, int month);
        Task<PeriodDto?> GetPeriodForDate(DateTime date);
    }
}