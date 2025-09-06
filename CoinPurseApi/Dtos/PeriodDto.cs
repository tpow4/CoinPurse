namespace CoinPurseApi.Dtos
{
    public class PeriodDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public bool IsCurrentWeek { get; set; }
        public string WeekRange { get; set; } = string.Empty; // e.g., "Jan 7 - Jan 13, 2024"
    }
}
