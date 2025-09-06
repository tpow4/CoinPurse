using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateInstitutionDto
    {
        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = string.Empty;
    }
}
