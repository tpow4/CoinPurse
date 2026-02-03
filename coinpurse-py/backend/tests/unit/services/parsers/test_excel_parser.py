"""
Unit tests for Excel parser
"""

import io

import pandas as pd

from services.parsers import ExcelParser


def create_excel_file(data: list[dict], columns: list[str]) -> io.BytesIO:
    """Helper to create an Excel file in memory"""
    df = pd.DataFrame(data, columns=columns)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer


class TestExcelParserBasic:
    """Basic Excel parsing tests"""

    def test_parse_simple_excel(self, chase_template_config):
        """Should parse a simple Excel file"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Post Date": "1/21/2026",
                "Description": "Test Payment",
                "Category": "",
                "Type": "Payment",
                "Amount": "100.00",
            },
        ]
        columns = [
            "Transaction Date",
            "Post Date",
            "Description",
            "Category",
            "Type",
            "Amount",
        ]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert len(rows) == 1
        assert rows[0].description == "Test Payment"
        assert rows[0].amount == 10000
        assert rows[0].transaction_type == "CREDIT"
        assert rows[0].is_valid

    def test_parse_negative_amounts(self, chase_template_config):
        """Should handle negative amounts"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Post Date": "1/21/2026",
                "Description": "Purchase",
                "Category": "Shopping",
                "Type": "Sale",
                "Amount": "-50.00",
            },
        ]
        columns = [
            "Transaction Date",
            "Post Date",
            "Description",
            "Category",
            "Type",
            "Amount",
        ]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert rows[0].amount == -5000
        assert rows[0].transaction_type == "DEBIT"

    def test_parse_multiple_rows(self, chase_template_config):
        """Should parse multiple rows"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Post Date": "1/21/2026",
                "Description": "Payment",
                "Category": "",
                "Amount": "100.00",
            },
            {
                "Transaction Date": "1/22/2026",
                "Post Date": "1/22/2026",
                "Description": "Purchase 1",
                "Category": "Food",
                "Amount": "-25.00",
            },
            {
                "Transaction Date": "1/23/2026",
                "Post Date": "1/23/2026",
                "Description": "Purchase 2",
                "Category": "Gas",
                "Amount": "-40.00",
            },
        ]
        columns = ["Transaction Date", "Post Date", "Description", "Category", "Amount"]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert len(rows) == 3
        assert rows[0].amount == 10000
        assert rows[1].amount == -2500
        assert rows[2].amount == -4000


class TestExcelParserInverted:
    """Tests for inverted sign convention (Discover)"""

    def test_parse_inverted_payment(self, discover_template_config):
        """Inverted: negative becomes positive"""
        data = [
            {
                "Trans. Date": "1/19/2026",
                "Post Date": "1/19/2026",
                "Description": "DIRECTPAY",
                "Amount": "-15.29",
                "Category": "Payments",
            },
        ]
        columns = ["Trans. Date", "Post Date", "Description", "Amount", "Category"]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=discover_template_config["column_mappings"],
            amount_config=discover_template_config["amount_config"],
            date_format=discover_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert rows[0].amount == 1529  # Inverted
        assert rows[0].transaction_type == "CREDIT"

    def test_parse_inverted_purchase(self, discover_template_config):
        """Inverted: positive becomes negative"""
        data = [
            {
                "Trans. Date": "1/18/2026",
                "Post Date": "1/18/2026",
                "Description": "RESTAURANT",
                "Amount": "17.76",
                "Category": "Restaurants",
            },
        ]
        columns = ["Trans. Date", "Post Date", "Description", "Amount", "Category"]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=discover_template_config["column_mappings"],
            amount_config=discover_template_config["amount_config"],
            date_format=discover_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert rows[0].amount == -1776  # Inverted
        assert rows[0].transaction_type == "DEBIT"


class TestExcelParserSplitColumns:
    """Tests for split columns sign convention (Capital One)"""

    def test_parse_credit_column(self, capital_one_template_config):
        """Credit column should be positive"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Posted Date": "1/21/2026",
                "Card No.": "1111",
                "Description": "PAYMENT",
                "Category": "Payment/Credit",
                "Debit": "",
                "Credit": "100.00",
            },
        ]
        columns = [
            "Transaction Date",
            "Posted Date",
            "Card No.",
            "Description",
            "Category",
            "Debit",
            "Credit",
        ]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=capital_one_template_config["column_mappings"],
            amount_config=capital_one_template_config["amount_config"],
            date_format=capital_one_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert rows[0].amount == 10000
        assert rows[0].transaction_type == "CREDIT"

    def test_parse_debit_column(self, capital_one_template_config):
        """Debit column should be negative"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Posted Date": "1/21/2026",
                "Card No.": "1111",
                "Description": "PURCHASE",
                "Category": "Shopping",
                "Debit": "50.00",
                "Credit": "",
            },
        ]
        columns = [
            "Transaction Date",
            "Posted Date",
            "Card No.",
            "Description",
            "Category",
            "Debit",
            "Credit",
        ]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=capital_one_template_config["column_mappings"],
            amount_config=capital_one_template_config["amount_config"],
            date_format=capital_one_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert rows[0].amount == -5000
        assert rows[0].transaction_type == "DEBIT"


class TestExcelParserValidation:
    """Validation tests for Excel parser"""

    def test_missing_description(self, chase_template_config):
        """Missing description should create validation error"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Post Date": "1/21/2026",
                "Description": "",
                "Category": "",
                "Amount": "100.00",
            },
        ]
        columns = ["Transaction Date", "Post Date", "Description", "Category", "Amount"]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert not rows[0].is_valid
        assert "Description is required" in rows[0].validation_errors

    def test_row_numbers(self, chase_template_config):
        """Row numbers should be correct"""
        data = [
            {
                "Transaction Date": "1/21/2026",
                "Post Date": "1/21/2026",
                "Description": "Row 1",
                "Category": "",
                "Amount": "100.00",
            },
            {
                "Transaction Date": "1/22/2026",
                "Post Date": "1/22/2026",
                "Description": "Row 2",
                "Category": "",
                "Amount": "200.00",
            },
        ]
        columns = ["Transaction Date", "Post Date", "Description", "Category", "Amount"]
        excel_file = create_excel_file(data, columns)

        parser = ExcelParser(
            column_mappings=chase_template_config["column_mappings"],
            amount_config=chase_template_config["amount_config"],
            date_format=chase_template_config["date_format"],
        )

        rows = parser.parse(excel_file)

        assert rows[0].row_number == 2  # After header
        assert rows[1].row_number == 3
