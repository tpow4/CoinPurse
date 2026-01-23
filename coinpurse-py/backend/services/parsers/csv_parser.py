"""
CSV file parser
"""

from typing import Any, BinaryIO

import pandas as pd

from .base_parser import BaseParser, ParsedRow


class CsvParser(BaseParser):
    """Parser for CSV files"""

    def __init__(
        self,
        column_mappings: dict[str, Any],
        amount_config: dict[str, Any],
        date_format: str = "%m/%d/%Y",
        header_row: int = 1,
        skip_rows: int = 0,
    ):
        super().__init__(column_mappings, amount_config, date_format, header_row, skip_rows)

    def parse(self, file: BinaryIO) -> list[ParsedRow]:
        """
        Parse a CSV file and return a list of ParsedRow objects

        Args:
            file: Binary file object to parse

        Returns:
            List of ParsedRow objects
        """
        # header_row is 1-indexed in our config, pandas uses 0-indexed
        header_idx = self.header_row - 1

        # Calculate rows to skip after header
        skiprows = None
        if self.skip_rows > 0:
            # Skip rows after header
            skiprows = list(range(self.header_row, self.header_row + self.skip_rows))

        # Read CSV file
        df = pd.read_csv(
            file,
            header=header_idx,
            skiprows=skiprows,
            dtype=str,  # Read all as strings to prevent type coercion issues
            keep_default_na=False,  # Don't convert empty strings to NaN
            na_values=[""],  # Only treat empty string as NA
        )

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        return self._process_dataframe(df)
