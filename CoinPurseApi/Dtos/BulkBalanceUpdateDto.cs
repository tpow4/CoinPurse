using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class BulkBalanceUpdateDto
    {
        public int? PeriodId { get; set; } // Optional - if null, uses current week
        
        [Required]
        [MinLength(1, ErrorMessage = "At least one account balance is required")]
        public List<CreateAccountBalanceDto> AccountBalances { get; set; } = new();
    }
}
