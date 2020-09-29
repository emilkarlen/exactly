from typing import List, Callable, TypeVar

CELL_AS_LINES = List[str]
CELL = TypeVar('CELL')


def derive_column_max_widths(cell_formatter_for_given_width: Callable[[int], Callable[[CELL], CELL_AS_LINES]],
                             available_width: int,
                             columns_with_cell_content: List[List[CELL]],
                             ) -> List[int]:
    cell_formatter = cell_formatter_for_given_width(
        available_width + _ADDITIONAL_WIDTH_TO_MAKE_WIDTH_LESS_LIKELY_TO_DEPEND_ON_WORD_WRAP)
    columns_with_cell_lines_str = [
        [cell_formatter(cell) for cell in col]
        for col in columns_with_cell_content
    ]
    columns_with_cell_lines_width = []
    for col in columns_with_cell_lines_str:
        col_lines = []
        for cell in col:
            for line in cell:
                col_lines.append(len(line))
        columns_with_cell_lines_width.append(col_lines)
    return [max(line_widths, default=0) for line_widths in columns_with_cell_lines_width]


_ADDITIONAL_WIDTH_TO_MAKE_WIDTH_LESS_LIKELY_TO_DEPEND_ON_WORD_WRAP = 100
