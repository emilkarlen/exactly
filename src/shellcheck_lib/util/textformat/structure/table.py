from shellcheck_lib.util.textformat.structure.core import ParagraphItem


class TableFormat:
    def __init__(self,
                 column_separator: str):
        self._column_separator = column_separator

    @property
    def column_separator(self) -> str:
        return self._column_separator


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
