namespace CoinPurseApi.Dtos
{
    public class BalanceDto
    {
        public DateTime Timestamp { get; set; }
        public int AccountId { get; set; }
        public string AccountName { get; set; } = string.Empty;
        public int Amount { get; set; }
    }
}
