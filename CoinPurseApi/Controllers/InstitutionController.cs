using CoinPurseApi.Dtos;
using CoinPurseApi.Services;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class InstitutionController(
        IInstitutionService institutionService,
        ILogger<InstitutionController> logger) : ControllerBase
    {
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<InstitutionDto>), StatusCodes.Status200OK)]
        public async Task<ActionResult<IEnumerable<InstitutionDto>>> GetInstitutions()
        {
            var institutions = await institutionService.GetInstitutionsAsync();
            return Ok(institutions);
        }

        [HttpGet("{id}")]
        [ProducesResponseType(typeof(InstitutionDto), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<InstitutionDto>> GetInstitution(int id)
        {
            
            var institution = await institutionService.GetInstitutionAsync(id);
            if (institution == null)
            {
                return NotFound($"Institution with ID {id} not found");
            }

            return Ok(institution);
        }

        [HttpPost]
        [ProducesResponseType(typeof(InstitutionDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<InstitutionDto>> CreateInstitution(CreateInstitutionDto institutionDto)
        {  
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var institution = await institutionService.CreateInstitutionAsync(institutionDto);

            return CreatedAtAction(
                nameof(GetInstitution),
                new { id = institution.Id },
                institution);
        }

        [HttpGet("{id}/accounts")]
        [ProducesResponseType(typeof(IEnumerable<AccountDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<IEnumerable<AccountDto>>> GetInstitutionAccounts(int id)
        {
            var institution = await institutionService.GetInstitutionAsync(id);
            if (institution == null)
            {
                return NotFound($"Institution with ID {id} not found");
            }

            var accounts = await institutionService.GetInstitutionAccountsAsync(id);
            return Ok(accounts);
        }
    }
}
