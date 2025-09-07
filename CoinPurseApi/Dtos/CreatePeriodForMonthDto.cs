using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreatePeriodForMonthDto
    {
        [Required]
        public int Year { get; set; }

        [Required]
        [Range(1, 12)]
        public int Month { get; set; }
    }
}
