namespace CoinPurseApi.Dtos
{
    public class CreateAccountBalanceDto
    {
        public int PeriodId { get; set; }
        public int AccountId { get; set; }
        public int Amount { get; set; }
    }
}
