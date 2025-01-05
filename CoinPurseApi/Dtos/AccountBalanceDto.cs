namespace CoinPurseApi.Dtos
{
    public class AccountBalanceDto
    {
        public int PeriodId { get; set; }
        public int AccountId { get; set; }
        public string AccountName { get; set; } = string.Empty;
        public int Amount { get; set; }
    }
}
