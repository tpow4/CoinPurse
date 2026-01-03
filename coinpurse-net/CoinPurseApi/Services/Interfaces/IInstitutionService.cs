using CoinPurseApi.Dtos;

namespace CoinPurseApi.Services.Interfaces
{
    public interface IInstitutionService
    {
        Task<InstitutionDto> GetInstitutionAsync(int id);
        Task<IEnumerable<InstitutionDto>> GetInstitutionsAsync();
        Task<InstitutionDto> CreateInstitutionAsync(CreateInstitutionDto institutionDto);
        Task<IEnumerable<AccountDto>> GetInstitutionAccountsAsync(int institutionId);
    }
}
