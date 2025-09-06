using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services
{
    public interface IPeriodService
    {
        Task<IEnumerable<PeriodDto>> GetPeriods();
    }
}
