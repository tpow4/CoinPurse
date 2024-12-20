﻿using System.ComponentModel.DataAnnotations;

namespace CoinPurseApi.Models
{
    public class Account
    {
        public int Id { get; set; }
        [Required]
        [MaxLength(100)]
        public required string Name { get; set; }
        public int TaxTypeId { get; set; }
        public int InstitutionId { get; set; }
        public bool IsActive { get; set; }

        public Institution Institution { get; set; }
        public ICollection<Balance> Balances { get; set; } = [];
    }
}
