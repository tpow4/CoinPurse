"""
Base parser interface for file parsing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, BinaryIO

import pandas as pd


@dataclass
class ParsedRow:
    """Represents a single parsed row from an import file"""

    row_number: int
    transaction_date: date | None = None
    posted_date: date | None = None
    description: str = ""
    amount: int = 0  # Amount in cents
    transaction_type: str = ""  # CREDIT or DEBIT
    bank_category: str | None = None
    validation_errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if the row has no validation errors"""
        return len(self.validation_errors) == 0


class BaseParser(ABC):
    """Abstract base class for file parsers"""

    def __init__(
        self,
        column_mappings: dict[str, Any],
        amount_config: dict[str, Any],
        date_format: str = "%m/%d/%Y",
        header_row: int = 1,
        skip_rows: int = 0,
    ):
        """
        Initialize the parser with template configuration

        Args:
            column_mappings: Dict mapping internal field names to file column names
            amount_config: Dict with sign convention and amount parsing settings
            date_format: strptime format string for parsing dates
            header_row: Row number where headers are located (1-indexed)
            skip_rows: Number of rows to skip after header
        """
        self.column_mappings = column_mappings
        self.amount_config = amount_config
        # Normalize accidental JSON/string wrapping like "\"%Y-%m-%d\""
        # so parser behavior remains stable even with slightly malformed template data.
        self.date_format = str(date_format).strip().strip("\"'")
        self.header_row = header_row
        self.skip_rows = skip_rows

    @abstractmethod
    def parse(self, file: BinaryIO) -> list[ParsedRow]:
        """
        Parse the file and return a list of ParsedRow objects

        Args:
            file: Binary file object to parse

        Returns:
            List of ParsedRow objects
        """
        pass

    def _process_dataframe(self, df: pd.DataFrame) -> list[ParsedRow]:
        """
        Process a pandas DataFrame into ParsedRow objects

        Args:
            df: DataFrame with raw data from file

        Returns:
            List of ParsedRow objects
        """
        rows = []
        for idx, row in df.iterrows():
            if self.header_row < 1:
                raise ValueError("header_row must be >= 1")
            if self.skip_rows < 0:
                raise ValueError("skip_rows must be >= 0")

            # Row number is 1-indexed, accounting for header and skip rows
            row_number = int(idx) + self.header_row + self.skip_rows + 1
            parsed = self._parse_row(row, row_number)
            rows.append(parsed)
        return rows

    def _parse_row(self, row: pd.Series, row_number: int) -> ParsedRow:
        """
        Parse a single row from the DataFrame

        Args:
            row: pandas Series representing a single row
            row_number: The row number in the original file

        Returns:
            ParsedRow object
        """
        errors: list[str] = []

        # Parse dates
        transaction_date = self._parse_date(
            row, self.column_mappings.get("transaction_date"), errors
        )
        posted_date = self._parse_date(
            row, self.column_mappings.get("posted_date"), errors
        )

        # Both dates are required
        if transaction_date is None:
            errors.append("Transaction date is required")
        if posted_date is None:
            errors.append("Posted date is required")

        # Parse description
        description = self._get_string_value(
            row, self.column_mappings.get("description"), ""
        )
        if not description:
            errors.append("Description is required")

        # Parse amount based on sign convention
        amount, transaction_type = self._parse_amount(row, errors)

        # Parse bank category (optional)
        bank_category = self._get_string_value(
            row, self.column_mappings.get("category"), None
        )

        return ParsedRow(
            row_number=row_number,
            transaction_date=transaction_date,
            posted_date=posted_date,
            description=description.strip() if description else "",
            amount=amount,
            transaction_type=transaction_type,
            bank_category=bank_category,
            validation_errors=errors,
        )

    def _parse_date(
        self, row: pd.Series, column_name: str | None, errors: list[str]
    ) -> date | None:
        """Parse a date value from a row"""
        if not column_name or column_name not in row.index:
            return None

        value = row[column_name]
        if pd.isna(value) or value == "":
            return None

        try:
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, date):
                return value
            # Parse string date
            return datetime.strptime(str(value).strip(), self.date_format).date()
        except ValueError:
            errors.append(f"Invalid date format in {column_name}: {value}")
            return None

    def _parse_amount(self, row: pd.Series, errors: list[str]) -> tuple[int, str]:
        """
        Parse amount based on sign convention

        Returns:
            Tuple of (amount in cents, transaction_type)
        """
        sign_convention = self.amount_config.get("sign_convention", "bank_standard")
        decimal_places = self.amount_config.get("decimal_places", 2)

        try:
            if sign_convention == "split_columns":
                return self._parse_split_columns(row, decimal_places)
            elif sign_convention == "inverted":
                return self._parse_inverted(row, decimal_places)
            elif sign_convention == "amount_with_type_column":
                return self._parse_amount_with_type(row, decimal_places)
            else:  # bank_standard
                return self._parse_bank_standard(row, decimal_places)
        except Exception as e:
            errors.append(f"Error parsing amount: {e}")
            return (0, "DEBIT")

    def _parse_bank_standard(
        self, row: pd.Series, decimal_places: int
    ) -> tuple[int, str]:
        """Parse amount with bank standard convention (positive=in, negative=out)"""
        amount_col = self.column_mappings.get("amount")
        raw_amount = self._get_numeric_value(row, amount_col, 0.0)
        amount_cents = self._to_cents(raw_amount, decimal_places)
        transaction_type = "CREDIT" if amount_cents >= 0 else "DEBIT"
        return (amount_cents, transaction_type)

    def _parse_inverted(self, row: pd.Series, decimal_places: int) -> tuple[int, str]:
        """Parse amount with inverted convention (multiply by -1)"""
        amount_col = self.column_mappings.get("amount")
        raw_amount = self._get_numeric_value(row, amount_col, 0.0)
        # Invert the sign
        raw_amount = -raw_amount
        amount_cents = self._to_cents(raw_amount, decimal_places)
        transaction_type = "CREDIT" if amount_cents >= 0 else "DEBIT"
        return (amount_cents, transaction_type)

    def _parse_split_columns(
        self, row: pd.Series, decimal_places: int
    ) -> tuple[int, str]:
        """Parse amount from separate debit/credit columns"""
        debit_col = self.amount_config.get("debit_column") or self.column_mappings.get(
            "debit"
        )
        credit_col = self.amount_config.get(
            "credit_column"
        ) or self.column_mappings.get("credit")

        debit_amount = self._get_numeric_value(row, debit_col, 0.0)
        credit_amount = self._get_numeric_value(row, credit_col, 0.0)

        if credit_amount > 0:
            # Credit = positive (money in)
            amount_cents = self._to_cents(credit_amount, decimal_places)
            return (amount_cents, "CREDIT")
        else:
            # Debit = negative (money out)
            amount_cents = self._to_cents(-abs(debit_amount), decimal_places)
            return (amount_cents, "DEBIT")

    def _parse_amount_with_type(
        self, row: pd.Series, decimal_places: int
    ) -> tuple[int, str]:
        """Parse amount with separate type indicator column"""
        amount_col = self.column_mappings.get("amount")
        type_col = self.column_mappings.get("transaction_type")

        raw_amount = abs(self._get_numeric_value(row, amount_col, 0.0))
        type_value = self._get_string_value(row, type_col, "").lower()

        credit_indicator = self.amount_config.get("credit_indicator", "credit").lower()

        if credit_indicator in type_value:
            amount_cents = self._to_cents(raw_amount, decimal_places)
            return (amount_cents, "CREDIT")
        else:
            amount_cents = self._to_cents(-raw_amount, decimal_places)
            return (amount_cents, "DEBIT")

    def _get_string_value(
        self, row: pd.Series, column_name: str | None, default: str | None
    ) -> str | None:
        """Get a string value from a row, handling missing columns and NaN"""
        if not column_name or column_name not in row.index:
            return default
        value = row[column_name]
        if pd.isna(value):
            return default
        return str(value)

    def _get_numeric_value(
        self, row: pd.Series, column_name: str | None, default: float
    ) -> float:
        """Get a numeric value from a row, handling missing columns and NaN"""
        if not column_name or column_name not in row.index:
            return default
        value = row[column_name]
        if pd.isna(value) or value == "":
            return default
        try:
            # Handle string amounts with currency symbols and commas
            if isinstance(value, str):
                value = value.replace("$", "").replace(",", "").strip()
            return float(value)
        except (ValueError, TypeError):
            return default

    def _to_cents(self, amount: float, decimal_places: int) -> int:
        """Convert a float amount to cents (integer)"""
        multiplier = 10**decimal_places
        return int(round(amount * multiplier))
