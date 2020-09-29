from typing import List, Callable

from exactly_lib.util import tables
from exactly_lib.util.tables import extend_each_sub_list_to_max_sub_list_length
from exactly_lib.util.textformat.rendering.text.table.column_max_width import derive_column_max_widths, CELL_AS_LINES
from exactly_lib.util.textformat.rendering.text.table.width_distribution import distribute_width
from exactly_lib.util.textformat.structure.table import Table, empty_cell, TableCell


class TableFormatter:
    """
    Formats a single Table.
    """

    UNDER_LINE_CHARACTER = '-'

    def __init__(self,
                 cell_formatter_for_given_width: Callable[[int], Callable[[TableCell], CELL_AS_LINES]],
                 available_width: int,
                 table: Table):
        self.cell_formatter_for_given_width = cell_formatter_for_given_width
        self.available_width = available_width

        self.table = table
        if not table.rows:
            self.normalised_rows = []
            self.columns = []
        else:
            self.normalised_rows = tables.extend_each_sub_list_to_max_sub_list_length(table.rows, empty_cell())
            self.columns = tables.transpose(self.normalised_rows)

        self.num_column_separators = 0 if not self.normalised_rows else (len(self.normalised_rows[0]) - 1)
        self.available_width_for_column_contents = (available_width -
                                                    self.num_column_separators * len(table.format.column_separator))

    def apply(self) -> List[str]:
        if not self.normalised_rows:
            return []
        if len(self.normalised_rows[0]) == 0:
            return []
        if self.available_width_for_column_contents <= 0:
            return []
        column_widths = self._derive_column_content_widths()
        if 0 in column_widths:
            return []
        column_formatters = [self.cell_formatter_for_given_width(width) for width in column_widths]
        row_column_cell_lines = self._format_cell_contents(column_formatters)
        return self._combine_cell_contents_into_lines(row_column_cell_lines, column_widths)

    def _derive_column_content_widths(self) -> List[int]:
        columns_with_max_line_width = derive_column_max_widths(self.cell_formatter_for_given_width,
                                                               self.available_width_for_column_contents,
                                                               self.columns)
        return distribute_width(columns_with_max_line_width, self.available_width_for_column_contents)

    def _format_cell_contents(self,
                              column_formatters: List[Callable[[TableCell], CELL_AS_LINES]],
                              ) -> List[List[CELL_AS_LINES]]:
        ret_val = []
        for row in self.normalised_rows:
            ret_val_row = []
            for formatter, cell in zip(column_formatters, row):
                ret_val_row.append(formatter(cell))
            ret_val.append(ret_val_row)
        return ret_val

    def _combine_cell_contents_into_lines(self,
                                          rows: List[List[CELL_AS_LINES]],
                                          column_widths: List[int],
                                          ) -> List[str]:
        def fill_string_to_function(width: int) -> Callable[[str], str]:
            format = '%-' + str(width) + 's'
            return lambda s: format % s

        column_separator = self.table.format.column_separator
        cell_line_formatter_list = [fill_string_to_function(width) for width in column_widths]
        ret_val = []
        for row_idx, row_cells in enumerate(rows):
            if row_idx == 1 and self.table.format.first_row_is_header:
                ret_val.append(self._header_row_underline(column_widths))
            cells_with_equal_num_lines = extend_each_sub_list_to_max_sub_list_length(row_cells, '')
            num_lines_per_cell = len(cells_with_equal_num_lines[0])
            for line_idx in range(num_lines_per_cell):
                output_line_cell_contents = []
                for col_idx, col_line_formatter in enumerate(cell_line_formatter_list):
                    output_line_cell_contents.append(col_line_formatter(cells_with_equal_num_lines[col_idx][line_idx]))
                ret_val.append(column_separator.join(output_line_cell_contents))
        return ret_val

    def _header_row_underline(self, column_widths: List[int]) -> str:
        width_of_col_separators = self.num_column_separators * len(self.table.format.column_separator)
        width_of_col_contents = sum(column_widths)
        line_width = width_of_col_separators + width_of_col_contents
        return line_width * self.UNDER_LINE_CHARACTER
