using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Models
{
    [PrimaryKey(nameof(PeriodId), nameof(AccountId))]
    public class AccountPeriod
    {
        public int PeriodId { get; set; }
        public int AccountId { get; set; }
        public int Balance { get; set; }
        public DateTime CreatedAt { get; set; }

        public Account Account { get; set; }
        public Period Period { get; set; }
    }
}
