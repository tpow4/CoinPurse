using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateAccountBalanceDto
    {
        [Required]
        [Range(1, int.MaxValue, ErrorMessage = "PeriodId must be a positive number")]
        public int PeriodId { get; set; }
        
        [Required]
        [Range(1, int.MaxValue, ErrorMessage = "AccountId must be a positive number")]
        public int AccountId { get; set; }
        
        [Required]
        public int Amount { get; set; }
    }
}
