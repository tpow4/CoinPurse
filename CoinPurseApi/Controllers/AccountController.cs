using CoinPurseApi.Dtos;
using CoinPurseApi.Models;
using CoinPurseApi.Services;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AccountController : ControllerBase
    {
        private readonly IAccountService _accountService;
        private readonly ILogger<AccountController> _logger;

        public AccountController(IAccountService accountService, ILogger<AccountController> logger)
        {
            _accountService = accountService;
            _logger = logger;
        }

        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<AccountDto>), StatusCodes.Status200OK)]
        public async Task<ActionResult<IEnumerable<Account>>> GetAccounts()
        {
            var accounts = await _accountService.GetAccountsAsync();
            return Ok(accounts);
        }

        [HttpGet("{id}")]
        [ProducesResponseType(typeof(AccountDto), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<Account>> GetAccount(int id)
        {
            var account = await _accountService.GetAccountAsync(id);
            if (account == null)
            {
                return NotFound();
            }

            return Ok(account);
        }

        [HttpPost]
        [ProducesResponseType(typeof(AccountDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<Account>> CreateAccount(CreateAccountDto accountDto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var createdAccount = await _accountService.CreateAccountAsync(accountDto);
            return CreatedAtAction(nameof(GetAccount), new { id = createdAccount.Id }, createdAccount);
        }

        [HttpPut]
        [ProducesResponseType(typeof(AccountDto), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<AccountDto>> UpdateAccount(int id, UpdateAccountDto accountDto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            try
            {
                var updatedAccount = await _accountService.UpdateAccountAsync(id, accountDto);
                return Ok(updatedAccount);
            }
            catch (KeyNotFoundException)
            {
                return NotFound($"Account with ID {id} not found");
            }
        }

        [HttpDelete]
        [ProducesResponseType(StatusCodes.Status204NoContent)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<IActionResult> DeleteAccount(int id)
        {
            var result = await _accountService.DeleteAccountAsync(id);
            if (!result)
            {
                return NotFound($"Account with ID {id} not found");
            }

            return NoContent();
        }

        [HttpGet("{id}/balances")]
        [ProducesResponseType(typeof(IEnumerable<BalanceDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<IEnumerable<Balance>>> GetAccountBalances(int id)
        {
            var balances = await _accountService.GetAccountBalancesAsync(id);
            return Ok(balances);
        }
    }
}
