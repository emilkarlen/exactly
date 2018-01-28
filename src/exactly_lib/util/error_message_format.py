from typing import List

from exactly_lib.util.line_source import Line, LineSequence

_WHICH_IS_A_BUILTIN_SYMBOL = 'which is a builtin symbol'


def source_line(line: Line) -> str:
    return 'Line {}: `{}\''.format(line.line_number, line.text)


def source_lines(lines: LineSequence) -> str:
    return source_line(lines.first_line)


def source_line_sequence(source: LineSequence) -> List[str]:
    return list(source.lines)


def source_line_of_symbol(definition_source: LineSequence) -> str:
    if definition_source is None:
        return _WHICH_IS_A_BUILTIN_SYMBOL
    else:
        return source_lines(definition_source)


def defined_at_line__err_msg_lines(definition_source: LineSequence) -> list:
    if definition_source is None:
        return [_WHICH_IS_A_BUILTIN_SYMBOL]
    else:
        return [
            'defined at',
            source_lines(definition_source)
        ]
