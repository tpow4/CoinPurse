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

        public async Task<InstitutionDto> GetInstitutionAsync(int id)
        {
            var institution = await coinPurseDbContext.Institutions
                .Include(i => i.Accounts)
                .SingleAsync(i => i.Id == id && i.IsActive);

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
                throw new InvalidOperationException("An error occurred while creating the institution", ex);
            }
        }

        public async Task<IEnumerable<AccountDto>> GetInstitutionAccountsAsync(int institutionId)
        {
            var institution = await coinPurseDbContext.Institutions
                .Include(i => i.Accounts)
                .SingleAsync(i => i.Id == institutionId && i.IsActive);

            if(institution == null)
            {
                _logger.LogError("Institution with ID {InstitutionId} not found", institutionId);
                throw new KeyNotFoundException($"Institution with ID {institutionId} not found");
            }

            return institution.Accounts.Select(a => a.ToDto());
        }
    }
}
