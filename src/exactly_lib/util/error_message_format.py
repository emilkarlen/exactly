from exactly_lib.util.line_source import Line


def source_line(line: Line) -> str:
    return 'Line {}: `{}\''.format(line.line_number, line.text)


def defined_at_line__err_msg_lines(definition_source: Line) -> list:
    return [
        'defined at',
        source_line(definition_source)
    ]
