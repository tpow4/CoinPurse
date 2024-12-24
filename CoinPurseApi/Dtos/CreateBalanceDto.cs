namespace CoinPurseApi.Dtos
{
    public class CreateBalanceDto
    {
        public int PeriodId { get; set; }
        public int AccountId { get; set; }
        public int Balance { get; set; }
    }
}
