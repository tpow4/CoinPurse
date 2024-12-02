using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Models
{
    public class Institution
    {
        public int Id { get; set; }
        [Required]
        [MaxLength(100)]
        public required string Name { get; set; }
        public bool IsActive { get; set; }

        public ICollection<Account> Accounts { get; set; } = [];
    }
}
