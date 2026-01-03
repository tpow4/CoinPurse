using CoinPurseApi.Dtos;
using CoinPurseApi.Services.Interfaces;
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

        [HttpPost]
        [ProducesResponseType(typeof(PeriodDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<PeriodDto>> CreatePeriod(CreatePeriodDto createPeriodDto)
        {
            try
            {
                if (!ModelState.IsValid)
                {
                    return BadRequest(ModelState);
                }

                var period = await periodService.CreatePeriod(createPeriodDto);
                return CreatedAtAction(nameof(GetPeriods), period);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating period");
                return StatusCode(500, "An error occurred while creating the period");
            }
        }

        [HttpPost("for-month")]
        [ProducesResponseType(typeof(PeriodDto), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(PeriodDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<PeriodDto>> GetOrCreatePeriodForMonth(CreatePeriodForMonthDto dto)
        {
            try
            {
                if (!ModelState.IsValid)
                {
                    return BadRequest(ModelState);
                }

                var period = await periodService.GetOrCreatePeriodForMonth(dto.Year, dto.Month);
                return Ok(period);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error getting or creating period for month {Year}-{Month}", dto.Year, dto.Month);
                return StatusCode(500, "An error occurred while getting or creating the period");
            }
        }

        [HttpGet("for-date")]
        [ProducesResponseType(typeof(PeriodDto), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<PeriodDto>> GetPeriodForDate([FromQuery] DateTime date)
        {
            try
            {
                var period = await periodService.GetPeriodForDate(date);
                if (period == null)
                {
                    return NotFound($"No period found for date {date:yyyy-MM-dd}");
                }

                return Ok(period);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error fetching period for date {Date}", date);
                return StatusCode(500, "An error occurred while fetching the period");
            }
        }
    }
}