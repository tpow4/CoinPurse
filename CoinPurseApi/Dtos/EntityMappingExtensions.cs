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
                IsActive = account.IsActive,
                LatestBalance = account.AccountPeriods
                    ?.OrderByDescending(b => b.PeriodId)
                    .FirstOrDefault()
                    ?.Amount
            };
        }

        public static AccountBalanceDto ToDto(this AccountBalance balance)
        {
            return new AccountBalanceDto
            {
                PeriodId = balance.PeriodId,
                AccountId = balance.AccountId,
                Amount = balance.Amount
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

        public static AccountBalance ToEntity(this CreateAccountBalanceDto dto)
        {
            return new AccountBalance
            {
                PeriodId = dto.PeriodId,
                AccountId = dto.AccountId,
                Amount = dto.Amount,
                CreatedAt = DateTime.UtcNow
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

        public static Institution ToEntity(this CreateInstitutionDto dto)
        {
            return new Institution
            {
                Name = dto.Name,
                IsActive = true
            };
        }

        public static void UpdateEntity(this UpdateAccountDto dto, Account account)
        {
            account.Name = dto.Name;
            account.TaxTypeId = dto.TaxTypeId;
            account.IsActive = dto.IsActive;
        }

        public static PeriodDto ToDto(this Period period)
        {
            var now = DateTime.Now;
            var isCurrentWeek = period.StartDate.Date <= now.Date && period.EndDate.Date >= now.Date;

            return new PeriodDto
            {
                Id = period.Id,
                Name = period.Name,
                StartDate = period.StartDate,
                EndDate = period.EndDate,
                IsCurrentWeek = isCurrentWeek,
                WeekRange = $"{period.StartDate:MMM d} - {period.EndDate:MMM d, yyyy}"
            };
        }

        public static AccountBalance ToEntityFromBulk(this CreateAccountBalanceDto dto, int periodId)
        {
            return new AccountBalance
            {
                AccountId = dto.AccountId,
                PeriodId = periodId,
                Amount = dto.Amount,
                CreatedAt = DateTime.UtcNow
            };
        }

    }
}
