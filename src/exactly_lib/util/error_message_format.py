from exactly_lib.util.line_source import Line

_WHICH_IS_A_BUILTIN_SYMBOL = 'which is a builtin symbol'


def source_line(line: Line) -> str:
    return 'Line {}: `{}\''.format(line.line_number, line.text)


def source_line_of_symbol(definition_source: Line) -> str:
    if definition_source is None:
        return _WHICH_IS_A_BUILTIN_SYMBOL
    else:
        return source_line(definition_source)


def defined_at_line__err_msg_lines(definition_source: Line) -> list:
    if definition_source is None:
        return [_WHICH_IS_A_BUILTIN_SYMBOL]
    else:
        return [
            'defined at',
            source_line(definition_source)
        ]
