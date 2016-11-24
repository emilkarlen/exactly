import os


def lines_content(lines: list) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines) + '\n'


def lines_content_with_os_linesep(lines: list) -> str:
    return '' \
        if not lines \
        else os.linesep.join(lines) + os.linesep


def line_separated(lines: list) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines)
