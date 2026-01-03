using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreatePeriodDto
    {
        [Required]
        public string Name { get; set; } = string.Empty;

        [Required]
        public DateTime StartDate { get; set; }

        [Required]
        public DateTime EndDate { get; set; }
    }
}
