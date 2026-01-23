"""
Excel file parser
"""

from typing import Any, BinaryIO

import pandas as pd

from .base_parser import BaseParser, ParsedRow


class ExcelParser(BaseParser):
    """Parser for Excel files (.xlsx, .xls)"""

    def __init__(
        self,
        column_mappings: dict[str, Any],
        amount_config: dict[str, Any],
        date_format: str = "%m/%d/%Y",
        header_row: int = 1,
        skip_rows: int = 0,
        sheet_name: str | int = 0,
    ):
        super().__init__(column_mappings, amount_config, date_format, header_row, skip_rows)
        self.sheet_name = sheet_name

    def parse(self, file: BinaryIO) -> list[ParsedRow]:
        """
        Parse an Excel file and return a list of ParsedRow objects

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

        # Read Excel file
        df = pd.read_excel(
            file,
            sheet_name=self.sheet_name,
            header=header_idx,
            skiprows=skiprows,
            dtype=str,  # Read all as strings to prevent type coercion issues
            na_values=[""],  # Only treat empty string as NA
        )

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        return self._process_dataframe(df)
