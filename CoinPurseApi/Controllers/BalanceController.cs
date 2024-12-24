using CoinPurseApi.Dtos;
using CoinPurseApi.Services;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BalanceController : ControllerBase
    {
        private readonly IBalanceService _balanceService;
        private readonly ILogger<BalanceController> _logger;

        public BalanceController(IBalanceService balanceService, ILogger<BalanceController> logger)
        {
            _balanceService = balanceService;
            _logger = logger;
        }

        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<BalanceDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetBalances([FromQuery] int accountId,
        [FromQuery] int startPeriodId,
        [FromQuery] int endPeriodId)
        {
            var balances = await _balanceService.GetBalancesForRangeAsync(accountId, startPeriodId, endPeriodId);
            return Ok(balances);
        }

        [HttpPost]
        [ProducesResponseType(typeof(BalanceDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<BalanceDto>> CreateBalance(CreateBalanceDto balanceDto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var balance = await _balanceService.CreateBalanceAsync(balanceDto);

            return CreatedAtAction(
                nameof(GetBalances),
                new
                {
                    accountId = balance.AccountId,
                    startDate = balance.PeriodId,
                    endDate = balance.PeriodId
                },
                balance);
        }
    }
}
