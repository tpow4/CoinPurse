using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Models
{
    [PrimaryKey(nameof(Timestamp), nameof(AccountId))]
    public class Balance
    {
        public DateTime Timestamp { get; set; }
        public int AccountId { get; set; }
        public int Amount { get; set; }

        public Account Account { get; set; }
    }
}
