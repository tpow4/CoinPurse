namespace CoinPurseApi.Dtos
{
    public class AccountDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public int TaxTypeId { get; set; }
        public string InstitutionName { get; set; } = string.Empty;
        public int? LatestBalance { get; set; }
    }
}
