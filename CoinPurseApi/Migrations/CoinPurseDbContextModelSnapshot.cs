﻿// <auto-generated />
using System;
using CoinPurseApi.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

#nullable disable

namespace CoinPurseApi.Migrations
{
    [DbContext(typeof(CoinPurseDbContext))]
    partial class CoinPurseDbContextModelSnapshot : ModelSnapshot
    {
        protected override void BuildModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder.HasAnnotation("ProductVersion", "9.0.0");

            modelBuilder.Entity("CoinPurseApi.Models.Account", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<int>("InstitutionId")
                        .HasColumnType("INTEGER");

                    b.Property<bool>("IsActive")
                        .HasColumnType("INTEGER");

                    b.Property<string>("Name")
                        .IsRequired()
                        .HasMaxLength(100)
                        .HasColumnType("TEXT");

                    b.Property<int>("TaxTypeId")
                        .HasColumnType("INTEGER");

                    b.HasKey("Id");

                    b.HasIndex("InstitutionId");

                    b.ToTable("Accounts");
                });

            modelBuilder.Entity("CoinPurseApi.Models.Balance", b =>
                {
                    b.Property<DateTime>("Timestamp")
                        .HasColumnType("TEXT");

                    b.Property<int>("AccountId")
                        .HasColumnType("INTEGER");

                    b.Property<int>("Amount")
                        .HasColumnType("INTEGER");

                    b.HasKey("Timestamp", "AccountId");

                    b.HasIndex("AccountId");

                    b.ToTable("Balances");
                });

            modelBuilder.Entity("CoinPurseApi.Models.Institution", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<bool>("IsActive")
                        .HasColumnType("INTEGER");

                    b.Property<string>("Name")
                        .IsRequired()
                        .HasMaxLength(100)
                        .HasColumnType("TEXT");

                    b.HasKey("Id");

                    b.ToTable("Institutions");
                });

            modelBuilder.Entity("CoinPurseApi.Models.Account", b =>
                {
                    b.HasOne("CoinPurseApi.Models.Institution", "Institution")
                        .WithMany("Accounts")
                        .HasForeignKey("InstitutionId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Institution");
                });

            modelBuilder.Entity("CoinPurseApi.Models.Balance", b =>
                {
                    b.HasOne("CoinPurseApi.Models.Account", "Account")
                        .WithMany("Balances")
                        .HasForeignKey("AccountId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Account");
                });

            modelBuilder.Entity("CoinPurseApi.Models.Account", b =>
                {
                    b.Navigation("Balances");
                });

            modelBuilder.Entity("CoinPurseApi.Models.Institution", b =>
                {
                    b.Navigation("Accounts");
                });
#pragma warning restore 612, 618
        }
    }
}