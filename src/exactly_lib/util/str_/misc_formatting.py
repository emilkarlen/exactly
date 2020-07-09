import os
from typing import Sequence, List


def with_appended_new_lines(lines: Sequence[str]) -> List[str]:
    return [
        line + '\n'
        for line in lines
    ]


def lines_content(lines: Sequence[str]) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines) + '\n'


def lines_content_with_os_linesep(lines: Sequence[str]) -> str:
    return '' \
        if not lines \
        else os.linesep.join(lines) + os.linesep


def line_separated(lines: Sequence[str]) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines)


def inside_parens(x) -> str:
    return '(' + str(x) + ')'
