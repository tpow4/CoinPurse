using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateBalancesForMonthDto
    {
        [Required]
        public int Year { get; set; }

        [Required]
        [Range(1, 12)]
        public int Month { get; set; }

        [Required]
        public List<CreateAccountBalanceDto> Balances { get; set; } = new();
    }
}
