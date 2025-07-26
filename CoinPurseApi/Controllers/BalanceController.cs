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

        public BalanceController(IBalanceService balanceService)
        {
            _balanceService = balanceService;
        }

        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetAllBalances()
        {
            var balances = await _balanceService.GetAllBalancesAsync();
            return Ok(balances);
        }

        [HttpGet("{accountId}")]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetBalancesByAccountId(int accountId)
        {
            var balances = await _balanceService.GetBalancesByAccountIdAsync(accountId);
            return Ok(balances);
        }

        [HttpPost]
        [ProducesResponseType(typeof(AccountBalanceDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<AccountBalanceDto>> CreateBalance(CreateAccountBalanceDto balanceDto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var balance = await _balanceService.CreateBalanceAsync(balanceDto);

            return CreatedAtAction(
                nameof(GetBalancesByAccountId),
                new
                {
                    accountId = balance.AccountId,
                    startPeriodId = balance.PeriodId,
                    endPeriodId = balance.PeriodId
                },
                balance);
        }
    }
}
