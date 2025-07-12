using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class InstitutionService(CoinPurseDbContext coinPurseDbContext, ILogger<InstitutionService> logger) : IInstitutionService
    {
        public async Task<IEnumerable<InstitutionDto>> GetInstitutionsAsync()
        {
            var institutions = await coinPurseDbContext.Institutions
                .Include(i => i.Accounts)
                .Where(i => i.IsActive)
                .ToListAsync();

            return institutions.Select(a => a.ToDto());
        }

        public async Task<InstitutionDto> GetInstitutionAsync(int institutionId)
        {
            var institution = await coinPurseDbContext.Institutions
                .Include(i => i.Accounts)
                .SingleAsync(i => i.Id == institutionId && i.IsActive);

            return institution.ToDto();
        }

        public async Task<InstitutionDto> CreateInstitutionAsync(CreateInstitutionDto institutionDto)
        {
            var institution = institutionDto.ToEntity();

            try
            {
                coinPurseDbContext.Institutions.Add(institution);
                await coinPurseDbContext.SaveChangesAsync();

                // Reload the account with relations
                institution = await coinPurseDbContext.Institutions
                    .Include(i => i.Accounts)
                    .SingleAsync(i => i.Id == institution.Id && i.IsActive);

                return institution.ToDto();
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating institution");
                throw;
            }
        }

        public async Task<IEnumerable<AccountDto>> GetInstitutionAccountsAsync(int institutionId)
        {
            var institution = await coinPurseDbContext.Institutions
                .Include(i => i.Accounts)
                .SingleAsync(i => i.Id == institutionId && i.IsActive);

            if(institution == null)
            {
                //Todo: determine error logging here
                throw new KeyNotFoundException($"Institution with ID {institutionId} not found");
            }

            return institution.Accounts.ToList().Select(a => a.ToDto());
        }
    }
}
