using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services.Interfaces
{
    public interface IPeriodService
    {
        Task<IEnumerable<PeriodDto>> GetPeriods();
    }
}
