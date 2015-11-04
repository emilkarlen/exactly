import os


def lines_content(lines: list) -> str:
    return '' \
        if not lines \
        else os.linesep.join(lines) + os.linesep
