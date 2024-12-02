namespace CoinPurseApi.Dtos
{
    public class CreateBalanceDto
    {
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public int AccountId { get; set; }
        public int Amount { get; set; }
    }
}
