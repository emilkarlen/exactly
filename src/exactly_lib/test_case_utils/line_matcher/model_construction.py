from typing import Iterator, Tuple

from exactly_lib.type_system.logic.line_matcher import LineMatcherLine, FIRST_LINE_NUMBER


def model_iter_from_file_line_iter(lines: Iterator[str]) -> Iterator[LineMatcherLine]:
    """
    Gives a sequence of line matcher models, corresponding to input lines read from file.
    New lines are expected to appear only as last character of lines, or not at all, if
    last line is not ended with new line in the file.

    @:param strings: lines from an input source
    """
    return enumerate((l.rstrip('\n') for l in lines),
                     FIRST_LINE_NUMBER)


def original_and_model_iter_from_file_line_iter(lines: Iterator[str]) -> Iterator[Tuple[str, LineMatcherLine]]:
    """
    Gives a sequence of pairs, corresponding to each element in lines.
    (original line, line-matcher-model-for-line).

    See also docs of model_iter_from_file_line_iter.

    @:param strings: lines from an input source
    """
    return (
        (original, (line_num, original.rstrip('\n')))
        for line_num, original in enumerate(lines, FIRST_LINE_NUMBER)
    )
