using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Services
{
    public class InstitutionService : IInstitutionService
    {
        private readonly CoinPurseDbContext _context;
        private readonly ILogger<InstitutionService> _logger;

        public InstitutionService(CoinPurseDbContext coinPurseDbContext, ILogger<InstitutionService> logger)
        {
            _context = coinPurseDbContext;
            _logger = logger;
        }

        public async Task<IEnumerable<InstitutionDto>> GetInstitutionsAsync()
        {
            var institutions = await _context.Institutions
                .Include(i => i.Accounts)
                .Where(i => i.IsActive)
                .ToListAsync();

            return institutions.Select(a => a.ToDto());
        }

        public async Task<InstitutionDto> GetInstitutionAsync(int id)
        {
            var institution = await _context.Institutions
                .Include(i => i.Accounts)
                .FirstOrDefaultAsync(i => i.IsActive);

            return institution?.ToDto();
        }

        public async Task<InstitutionDto> CreateInstitutionAsync(CreateInstitutionDto institutionDto)
        {
            var institution = institutionDto.ToEntity();

            try
            {
                _context.Institutions.Add(institution);
                await _context.SaveChangesAsync();

                // Reload the account with relations
                institution = await _context.Institutions
                    .Include(i => i.Accounts)
                    .FirstAsync(i => i.Id == institution.Id);

                return institution.ToDto();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating institution");
                throw;
            }
        }

        public async Task<IEnumerable<AccountDto>> GetInstitutionAccountsAsync(int institutionId)
        {
            var institution = await _context.Institutions
                .Include(i => i.Accounts)
                .FirstOrDefaultAsync(i => i.IsActive);

            if(institution == null)
            {
                //Todo: determine error logging here
                throw new KeyNotFoundException($"Institution with ID {institutionId} not found");
            }

            return institution.Accounts.ToList().Select(a => a.ToDto());
        }
    }
}
