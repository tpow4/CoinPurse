using CoinPurseApi.Dtos;
using CoinPurseApi.Services;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PeriodController(IPeriodService periodService, ILogger<PeriodController> logger) : ControllerBase
    {
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<PeriodDto>), StatusCodes.Status200OK)]
        public async Task<ActionResult<IEnumerable<PeriodDto>>> GetPeriods()
        {
            try
            {
                var periods = await periodService.GetPeriods();
                return Ok(periods);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error fetching periods");
                return StatusCode(500, "An error occurred while fetching periods");
            }
        }
    }
}
