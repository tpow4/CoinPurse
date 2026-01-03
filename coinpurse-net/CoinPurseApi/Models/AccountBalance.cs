using Microsoft.EntityFrameworkCore;

namespace CoinPurseApi.Models
{
    [PrimaryKey(nameof(PeriodId), nameof(AccountId))]
    public class AccountBalance
    {
        public int PeriodId { get; set; }
        public int AccountId { get; set; }
        public int Amount { get; set; }
        public DateTime CreatedAt { get; set; }

        public Account? Account { get; set; }
        public Period? Period { get; set; }
    }
}
