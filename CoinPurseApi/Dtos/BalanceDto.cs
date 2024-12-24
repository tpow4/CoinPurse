namespace CoinPurseApi.Dtos
{
    public class BalanceDto
    {
        public int PeriodId { get; set; }
        public int AccountId { get; set; }
        public string AccountName { get; set; } = string.Empty;
        public int Balance { get; set; }
    }
}
