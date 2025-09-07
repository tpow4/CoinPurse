using CoinPurseApi.Dtos;
using CoinPurseApi.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BalanceController(IBalanceService balanceService, ILogger<BalanceController> logger) : ControllerBase
    {
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetAllBalances()
        {
            try
            {
                var balances = await balanceService.GetAllBalancesAsync();
                return Ok(balances);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error fetching balances");
                return StatusCode(500, "An error occurred while fetching balances");
            }
        }

        [HttpGet("{accountId}")]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetBalancesByAccountId(int accountId)
        {
            try
            {
                var balances = await balanceService.GetBalancesByAccountIdAsync(accountId);
                return Ok(balances);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error fetching balances for account {AccountId}", accountId);
                return StatusCode(500, "An error occurred while fetching balances");
            }
        }

        [HttpPost("for-month")]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<IEnumerable<AccountBalanceDto>>> CreateBalancesForMonth(CreateBalancesForMonthDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            if (dto.Balances == null || dto.Balances.Count == 0)
            {
                return BadRequest("At least one balance is required");
            }

            try
            {
                var balances = await balanceService.CreateBalancesForMonthAsync(dto);
                return CreatedAtAction(nameof(GetAllBalances), balances);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating balances for month {Year}-{Month}", dto.Year, dto.Month);
                return StatusCode(500, "An error occurred while creating balances for the month");
            }
        }

        [HttpPost("for-date")]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<IEnumerable<AccountBalanceDto>>> CreateBalancesForDate(CreateBalancesForDateDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            if (dto.Balances == null || dto.Balances.Count == 0)
            {
                return BadRequest("At least one balance is required");
            }

            try
            {
                var balances = await balanceService.CreateBalancesForDateAsync(dto);
                return CreatedAtAction(nameof(GetAllBalances), balances);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error creating balances for date {Date}", dto.TargetDate);
                return StatusCode(500, "An error occurred while creating balances for the date");
            }
        }
    }
}