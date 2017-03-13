from exactly_lib.util.line_source import Line


def source_line(line: Line) -> str:
    return 'Line {}: `{}\''.format(line.line_number, line.text)
