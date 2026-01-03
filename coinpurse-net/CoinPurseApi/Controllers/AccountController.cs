using CoinPurseApi.Dtos;
using CoinPurseApi.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace CoinPurseApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AccountController(IAccountService accountService, ILogger<AccountController> logger) : ControllerBase
    {
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<AccountDto>), StatusCodes.Status200OK)]
        public async Task<ActionResult<IEnumerable<AccountDto>>> GetAccounts()
        {
            var accounts = await accountService.GetAccountsAsync();
            return Ok(accounts);
        }

        [HttpGet("{id}")]
        [ProducesResponseType(typeof(AccountDto), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<AccountDto>> GetAccount(int id)
        {
            var account = await accountService.GetAccountAsync(id);
            if (account == null)
            {
                logger.LogWarning("Account with ID {Id} not found", id);
                return NotFound();
            }

            return Ok(account);
        }

        [HttpPost]
        [ProducesResponseType(typeof(AccountDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<AccountDto>> CreateAccount(CreateAccountDto accountDto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var createdAccount = await accountService.CreateAccountAsync(accountDto);
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
                var updatedAccount = await accountService.UpdateAccountAsync(id, accountDto);
                return Ok(updatedAccount);
            }
            catch (KeyNotFoundException)
            {
                logger.LogWarning("Attempted to update non-existent account with ID {Id}", id);
                return NotFound($"Account with ID {id} not found");
            }
        }

        [HttpDelete]
        [ProducesResponseType(StatusCodes.Status204NoContent)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<IActionResult> DeleteAccount(int id)
        {
            var result = await accountService.DeleteAccountAsync(id);
            if (!result)
            {
                logger.LogWarning("Attempted to delete non-existent account with ID {Id}", id);
                return NotFound($"Account with ID {id} not found");
            }

            return NoContent();
        }

        [HttpGet("{id}/balances")]
        [ProducesResponseType(typeof(IEnumerable<AccountBalanceDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<IEnumerable<AccountBalanceDto>>> GetAccountBalances(int id)
        {
            var balances = await accountService.GetAccountBalancesAsync(id);
            return Ok(balances);
        }
    }
}
