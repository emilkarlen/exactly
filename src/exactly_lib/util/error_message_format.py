from typing import List

from exactly_lib.util.line_source import LineSequence

_WHICH_IS_A_BUILTIN_SYMBOL = 'which is a builtin symbol'


def source_lines(lines: LineSequence) -> str:
    return 'Line {}:\n\n{}'.format(lines.first_line.line_number,
                                   lines.text)


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
