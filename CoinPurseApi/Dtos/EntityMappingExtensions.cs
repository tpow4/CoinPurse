using CoinPurseApi.Models;

namespace CoinPurseApi.Dtos
{
    public static class EntityMappingExtensions
    {
        public static AccountDto ToDto(this Account account)
        {
            return new AccountDto
            {
                Id = account.Id,
                Name = account.Name,
                TaxTypeId = account.TaxTypeId,
                InstitutionName = account.Institution?.Name ?? string.Empty,
                LatestBalance = account.Balances
                    ?.OrderByDescending(b => b.Timestamp)
                    .FirstOrDefault()
                    ?.Amount
            };
        }

        public static Account ToEntity(this CreateAccountDto dto)
        {
            return new Account
            {
                Name = dto.Name,
                TaxTypeId = dto.TaxTypeId,
                InstitutionId = dto.InstitutionId
            };
        }

        public static void UpdateEntity(this UpdateAccountDto dto, Account account)
        {
            account.Name = dto.Name;
            account.TaxTypeId = dto.TaxTypeId;
        }

        public static BalanceDto ToDto(this Balance balance)
        {
            return new BalanceDto
            {
                Timestamp = balance.Timestamp,
                AccountId = balance.AccountId,
                AccountName = balance.Account?.Name ?? string.Empty,
                Amount = balance.Amount
            };
        }

        public static Balance ToEntity(this CreateBalanceDto dto)
        {
            return new Balance
            {
                Timestamp = dto.Timestamp,
                AccountId = dto.AccountId,
                Amount = dto.Amount
            };
        }

        public static InstitutionDto ToDto(this Institution institution)
        {
            return new InstitutionDto
            {
                Id = institution.Id,
                Name = institution.Name,
                AccountCount = institution.Accounts?.Count ?? 0
            };
        }

        public static Institution ToEntity(this CreateInstitutionDto dto)
        {
            return new Institution
            {
                Name = dto.Name,
                IsActive = true
            };
        }
    }
}
