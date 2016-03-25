import types

from shellcheck_lib.util import tables
from shellcheck_lib.util.tables import extend_each_sub_list_to_max_sub_list_length
from shellcheck_lib.util.textformat.formatting.table.column_max_width import derive_column_max_widths
from shellcheck_lib.util.textformat.formatting.table.width_distribution import distribute_width
from shellcheck_lib.util.textformat.structure.table import Table


class TableFormatter:
    """
    Formats a single Table.
    """

    def __init__(self,
                 paragraph_items_formatter_for_given_width: types.FunctionType,
                 available_width: int,
                 table: Table):
        self.paragraph_items_formatter_for_given_width = paragraph_items_formatter_for_given_width
        self.available_width = available_width
        self.table = table
        if not table.rows:
            self.normalised_rows = []
            self.columns = []
        else:
            self.normalised_rows = tables.extend_each_sub_list_to_max_sub_list_length(table.rows, [])
            self.columns = tables.transpose(self.normalised_rows)

    def apply(self) -> list:
        if not self.table.rows:
            return []
        column_widths = self._derive_column_content_widths()
        column_formatters = [self.paragraph_items_formatter_for_given_width(width) for width in column_widths]
        row_column_cell_lines = self._format_cell_contents(column_formatters)
        return self._combine_cell_contents_into_lines(row_column_cell_lines, column_widths)

    def _derive_column_content_widths(self) -> list:
        columns_with_max_line_width = derive_column_max_widths(self.paragraph_items_formatter_for_given_width,
                                                               self.available_width,
                                                               self.columns)
        return distribute_width(columns_with_max_line_width, self.available_width)

    def _format_cell_contents(self, column_formatters):
        ret_val = []
        for row in self.normalised_rows:
            ret_val_row = []
            for formatter, cell in zip(column_formatters, row):
                ret_val_row.append(formatter(cell))
            ret_val.append(ret_val_row)
        return ret_val

    def _combine_cell_contents_into_lines(self, row_cell_lines: list, column_widths: list) -> list:
        def fill_string_to_function(width: int):
            format = '%-' + str(width) + 's'
            return lambda s: format % s

        column_separator = self.table.format.column_separator
        cell_line_formatter_list = [fill_string_to_function(width) for width in column_widths]
        ret_val = []
        for cells in row_cell_lines:
            cells_with_equal_num_lines = extend_each_sub_list_to_max_sub_list_length(cells, '')
            num_lines_per_cell = len(cells_with_equal_num_lines[0])
            for line_idx in range(num_lines_per_cell):
                output_line_cell_contents = []
                for col_idx, col_line_formatter in enumerate(cell_line_formatter_list):
                    output_line_cell_contents.append(col_line_formatter(cells_with_equal_num_lines[col_idx][line_idx]))
                ret_val.append(column_separator.join(output_line_cell_contents))
        return ret_val
