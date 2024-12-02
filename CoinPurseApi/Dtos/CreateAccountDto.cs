using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateAccountDto
    {
        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = string.Empty;
        public int TaxTypeId { get; set; }
        public int InstitutionId { get; set; }
    }
}
