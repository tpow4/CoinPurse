"""
Unit tests for CSV parser
"""

import io
from datetime import date

import pytest

from services.parsers import CsvParser


class TestCsvParserChase:
    """Tests for Chase Credit Card CSV format (bank_standard)"""

    def test_parse_payment_positive_amount(self, chase_template_config):
        """Payment should remain positive (CREDIT)"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,Payment Thank You-Mobile,,Payment,3153.72,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert rows[0].description == "Payment Thank You-Mobile"
        assert rows[0].amount == 315372  # $3153.72 in cents
        assert rows[0].transaction_type == "CREDIT"
        assert rows[0].is_valid

    def test_parse_purchase_negative_amount(self, chase_template_config):
        """Purchase should remain negative (DEBIT)"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,STEAMGAMES.COM,Entertainment,Sale,-6.9,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert rows[0].description == "STEAMGAMES.COM"
        assert rows[0].amount == -690  # -$6.90 in cents
        assert rows[0].transaction_type == "DEBIT"
        assert rows[0].bank_category == "Entertainment"
        assert rows[0].is_valid

    def test_parse_dates(self, chase_template_config):
        """Should parse both transaction and posted dates"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/15/2026,1/17/2026,Test Transaction,,Sale,-10.00,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert rows[0].transaction_date == date(2026, 1, 15)
        assert rows[0].posted_date == date(2026, 1, 17)

    def test_parse_empty_category(self, chase_template_config):
        """Empty category should be None"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,Payment Thank You,,Payment,100.00,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert rows[0].bank_category is None


class TestCsvParserDiscover:
    """Tests for Discover Credit Card CSV format (inverted)"""

    def test_parse_payment_inverted(self, discover_template_config):
        """Discover payment (-15.29) should become positive CREDIT"""
        csv_data = """Trans. Date,Post Date,Description,Amount,Category
1/19/2026,1/19/2026,DIRECTPAY FULL BALANCE,-15.29,Payments and Credits"""

        parser = CsvParser(
            column_mappings=discover_template_config["column_mappings"],
            amount_config=discover_template_config["amount_config"],
            date_format=discover_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert rows[0].amount == 1529  # Inverted: -15.29 -> +15.29 -> 1529 cents
        assert rows[0].transaction_type == "CREDIT"
        assert rows[0].bank_category == "Payments and Credits"

    def test_parse_purchase_inverted(self, discover_template_config):
        """Discover purchase (+17.76) should become negative DEBIT"""
        csv_data = """Trans. Date,Post Date,Description,Amount,Category
1/18/2026,1/18/2026,SQ *AXUM FOODS LLC,17.76,Restaurants"""

        parser = CsvParser(
            column_mappings=discover_template_config["column_mappings"],
            amount_config=discover_template_config["amount_config"],
            date_format=discover_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert rows[0].amount == -1776  # Inverted: +17.76 -> -17.76 -> -1776 cents
        assert rows[0].transaction_type == "DEBIT"
        assert rows[0].bank_category == "Restaurants"

    def test_parse_multiple_rows(self, discover_template_config):
        """Should parse multiple rows correctly"""
        csv_data = """Trans. Date,Post Date,Description,Amount,Category
1/19/2026,1/19/2026,DIRECTPAY FULL BALANCE,-15.29,Payments and Credits
1/18/2026,1/18/2026,SQ *AXUM FOODS LLC,17.76,Restaurants
1/17/2026,1/17/2026,AMAZON.COM,-5.00,Shopping"""

        parser = CsvParser(
            column_mappings=discover_template_config["column_mappings"],
            amount_config=discover_template_config["amount_config"],
            date_format=discover_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 3
        assert rows[0].amount == 1529  # Payment: CREDIT
        assert rows[1].amount == -1776  # Purchase: DEBIT
        assert rows[2].amount == 500  # Refund: CREDIT


class TestCsvParserCapitalOne:
    """Tests for Capital One Credit Card CSV format (split_columns)"""

    def test_parse_credit_column(self, capital_one_template_config):
        """Credit column value should be positive CREDIT"""
        csv_data = """Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
1/21/2026,1/21/2026,1111,CAPITAL ONE MOBILE PYMT,Payment/Credit,,2675.92"""

        parser = CsvParser(
            column_mappings=capital_one_template_config["column_mappings"],
            amount_config=capital_one_template_config["amount_config"],
            date_format=capital_one_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert rows[0].amount == 267592  # $2675.92 in cents, positive
        assert rows[0].transaction_type == "CREDIT"
        assert rows[0].bank_category == "Payment/Credit"

    def test_parse_debit_column(self, capital_one_template_config):
        """Debit column value should be negative DEBIT"""
        csv_data = """Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
1/15/2026,1/16/2026,1111,AMAZON PURCHASE,Shopping,49.99,"""

        parser = CsvParser(
            column_mappings=capital_one_template_config["column_mappings"],
            amount_config=capital_one_template_config["amount_config"],
            date_format=capital_one_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert rows[0].amount == -4999  # $49.99 in cents, negative
        assert rows[0].transaction_type == "DEBIT"

    def test_parse_mixed_transactions(self, capital_one_template_config):
        """Should handle mix of credits and debits"""
        csv_data = """Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
1/21/2026,1/21/2026,1111,PAYMENT,Payment/Credit,,100.00
1/20/2026,1/20/2026,1111,GROCERY STORE,Groceries,50.00,
1/19/2026,1/19/2026,1111,REFUND,Refund,,25.00"""

        parser = CsvParser(
            column_mappings=capital_one_template_config["column_mappings"],
            amount_config=capital_one_template_config["amount_config"],
            date_format=capital_one_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 3
        assert rows[0].amount == 10000  # Credit: +$100
        assert rows[0].transaction_type == "CREDIT"
        assert rows[1].amount == -5000  # Debit: -$50
        assert rows[1].transaction_type == "DEBIT"
        assert rows[2].amount == 2500  # Credit: +$25
        assert rows[2].transaction_type == "CREDIT"


class TestCsvParserValidation:
    """Tests for validation and error handling"""

    def test_missing_description_error(self, chase_template_config):
        """Missing description should add validation error"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,,,Sale,-10.00,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert len(rows) == 1
        assert not rows[0].is_valid
        assert "Description is required" in rows[0].validation_errors

    def test_missing_both_dates_error(self, chase_template_config):
        """Missing date mappings should add validation errors"""
        # Create config with no date mappings
        config = chase_template_config.copy()
        config["column_mappings"] = {
            "description": "Description",
            "amount": "Amount",
        }

        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,Test Transaction,,Sale,-10.00,"""

        parser = CsvParser(
            column_mappings=config["column_mappings"],
            amount_config=config["amount_config"],
            date_format=config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert not rows[0].is_valid
        assert "Transaction date is required" in rows[0].validation_errors
        assert "Posted date is required" in rows[0].validation_errors

    def test_invalid_date_format_error(self, chase_template_config):
        """Invalid date format should add validation error"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
not-a-date,1/21/2026,Test Transaction,,Sale,-10.00,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert rows[0].transaction_date is None
        assert "Invalid date format" in rows[0].validation_errors[0]
        assert "Transaction date is required" in rows[0].validation_errors
        assert rows[0].posted_date == date(2026, 1, 21)

    def test_row_numbers_correct(self, chase_template_config):
        """Row numbers should be correct (1-indexed, accounting for header)"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,Row 1,,Sale,-10.00,
1/22/2026,1/22/2026,Row 2,,Sale,-20.00,
1/23/2026,1/23/2026,Row 3,,Sale,-30.00,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert rows[0].row_number == 2  # First data row after header
        assert rows[1].row_number == 3
        assert rows[2].row_number == 4

    def test_whitespace_in_column_names(self, chase_template_config):
        """Should handle whitespace in column names"""
        csv_data = """Transaction Date , Post Date , Description , Category , Type , Amount , Memo
1/21/2026,1/21/2026,Test,,Sale,-10.00,"""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert rows[0].description == "Test"
        assert rows[0].is_valid

    def test_currency_symbols_in_amount(self, chase_template_config):
        """Should handle currency symbols and commas in amounts"""
        csv_data = """Transaction Date,Post Date,Description,Category,Type,Amount,Memo
1/21/2026,1/21/2026,Big Purchase,,Sale,"$-1,234.56","""

        parser = CsvParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(io.BytesIO(csv_data.encode("utf-8")))

        assert rows[0].amount == -123456  # -$1,234.56 in cents
        assert rows[0].is_valid
