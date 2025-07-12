using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Models
{
    public class Account
    {
        public int Id { get; set; }
        [Required]
        [MaxLength(100)]
        public required string Name { get; set; }
        public int TaxTypeId { get; set; }
        public int InstitutionId { get; set; }
        public bool IsActive { get; set; }

        public required Institution Institution { get; set; }
        public ICollection<AccountBalance> AccountPeriods { get; set; } = [];
    }

    public enum TaxType
    {
        Standard = 1,
        Roth = 2,
        Traditional = 3,
        TaxFree = 4
    }
}
