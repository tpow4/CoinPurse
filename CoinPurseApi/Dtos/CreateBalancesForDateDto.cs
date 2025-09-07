using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateBalancesForDateDto
    {
        [Required]
        public DateTime TargetDate { get; set; }

        [Required]
        public List<CreateAccountBalanceDto> Balances { get; set; } = new();
    }
}
