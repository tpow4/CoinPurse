using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Models
{
    public class Institution
    {
        public int Id { get; set; }
        [Required]
        public string Name { get; set; }

        public Account Account { get; set; }
    }
}
