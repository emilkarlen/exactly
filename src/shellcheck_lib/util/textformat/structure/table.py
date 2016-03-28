from shellcheck_lib.util.textformat.structure.core import ParagraphItem


class TableFormat:
    def __init__(self,
                 column_separator: str,
                 first_row_is_header: bool = False,
                 first_column_is_header: bool = False):
        self._column_separator = column_separator
        self._first_row_is_header = first_row_is_header
        self._first_column_is_header = first_column_is_header

    @property
    def column_separator(self) -> str:
        return self._column_separator

    @property
    def first_row_is_header(self) -> bool:
        return self._first_row_is_header

    @property
    def first_column_is_header(self) -> bool:
        return self._first_column_is_header


class Table(ParagraphItem):
    def __init__(self,
                 format_: TableFormat,
                 rows: list):
        """
        :param rows: [[ParagraphItem]]
        """
        self._format = format_
        self._rows = rows

    @property
    def format(self) -> TableFormat:
        return self._format

    @property
    def rows(self) -> list:
        return self._rows


def single_paragraph_cell(paragraph_item: ParagraphItem) -> list:
    return [paragraph_item]


def empty_cell() -> list:
    return []
