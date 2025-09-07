using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateAccountBalanceDto
    {
        [Required]
        public int AccountId { get; set; }

        [Required]
        public int Amount { get; set; }
    }
}
