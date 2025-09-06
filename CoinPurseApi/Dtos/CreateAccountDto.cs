using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Dtos
{
    public class CreateAccountDto
    {
        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = string.Empty;
        [Range(1, int.MaxValue, ErrorMessage = "TaxTypeId must be a positive number")]
        public int TaxTypeId { get; set; }
        
        [Range(1, int.MaxValue, ErrorMessage = "InstitutionId must be a positive number")]
        public int InstitutionId { get; set; }
    }
}
