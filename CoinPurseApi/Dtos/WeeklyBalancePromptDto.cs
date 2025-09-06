namespace CoinPurseApi.Dtos
{
    public class WeeklyBalancePromptDto
    {
        public PeriodDto CurrentWeekPeriod { get; set; } = new();
        public bool HasBalancesEntered { get; set; }
        public List<AccountDto> AccountsNeedingBalances { get; set; } = new();
        public DateTime LastEntryDate { get; set; }
    }
}
