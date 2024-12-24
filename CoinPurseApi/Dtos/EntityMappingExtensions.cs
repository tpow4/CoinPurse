﻿using CoinPurseApi.Models;

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
                LatestBalance = account.AccountPeriods
                    ?.OrderByDescending(b => b.PeriodId)
                    .FirstOrDefault()
                    ?.Balance
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

        public static BalanceDto ToDto(this AccountPeriod balance)
        {
            return new BalanceDto
            {
                PeriodId = balance.PeriodId,
                AccountId = balance.AccountId,
                AccountName = balance.Account?.Name ?? string.Empty,
                Balance = balance.Balance
            };
        }

        public static AccountPeriod ToEntity(this CreateBalanceDto dto)
        {
            return new AccountPeriod
            {
                PeriodId = dto.PeriodId,
                AccountId = dto.AccountId,
                Balance = dto.Balance,
                CreatedAt = DateTime.UtcNow
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
