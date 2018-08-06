from typing import List

from exactly_lib.util.line_source import LineSequence


def source_lines(lines: LineSequence) -> str:
    return 'Line {}:\n\n{}'.format(lines.first_line.line_number,
                                   lines.text)


def source_line_sequence(source: LineSequence) -> List[str]:
    return list(source.lines)
