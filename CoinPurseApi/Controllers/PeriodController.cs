using CoinPurseApi.Data;
using CoinPurseApi.Dtos;
using CoinPurseApi.Models;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PeriodController : ControllerBase
    {
        private readonly CoinPurseDbContext _context;
        private readonly ILogger<PeriodController> _logger;

        public PeriodController(CoinPurseDbContext context, ILogger<PeriodController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<PeriodDto>), StatusCodes.Status200OK)]
        public ActionResult<IEnumerable<PeriodDto>> GetPeriods()
        {
            try
            {
                var periods = await _context.Periods
                    .Select(p => new PeriodDto
                    {
                        Id = p.Id,
                        Name = p.Name,
                        StartDate = p.StartDate,
                        EndDate = p.EndDate
                    })
                    .OrderBy(p => p.Id)
                    .ToListAsync();
                return Ok(periods);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching periods");
                return StatusCode(500, "An error occurred while fetching periods");
            }
        }
    }
}
