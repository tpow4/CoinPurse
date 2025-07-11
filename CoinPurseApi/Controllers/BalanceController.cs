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

        // Bulk create balances
        [HttpPost("bulk")]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<IEnumerable<AccountBalanceDto>>> CreateBalancesBulk([FromBody] List<CreateAccountBalanceDto> balancesDto)
        {
            if (balancesDto == null || balancesDto.Count == 0)
            {
                return BadRequest("No balances provided");
            }

            var createdBalances = new List<AccountBalanceDto>();
            foreach (var dto in balancesDto)
            {
                if (dto == null)
                {
                    return BadRequest("Invalid balance data provided");
                }
                var created = await _balanceService.CreateBalanceAsync(dto);
                createdBalances.Add(created);
            }
            return Created("/api/balance/bulk", createdBalances);
        }
    }
}
