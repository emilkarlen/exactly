def lines_content(lines: list) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines) + '\n'


def line_separated(lines: list) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines)
