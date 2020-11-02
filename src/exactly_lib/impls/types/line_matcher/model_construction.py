from typing import Iterator, Tuple, Callable

from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine, FIRST_LINE_NUMBER
from exactly_lib.util.functional import map_optional
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib.util.interval.w_inversion import intervals
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion

LINES_INTERVAL_FOR_UNKNOWN_INTERVAL = intervals.unlimited_with_unlimited_inversion()

FullContentsAndLineMatcherLine = Tuple[str, LineMatcherLine]


def adapt_to_line_num_range(interval: IntIntervalWInversion) -> IntIntervalWInversion:
    """
    :return: All non-None values >= FIRST_LINE_NUMBER.
    lower > FIRST_LINE_NUMBER (if not None)
    """
    if interval.is_empty:
        return interval
    if interval.upper is not None and interval.upper < FIRST_LINE_NUMBER:
        return intervals.Empty()

    lower = map_optional(_adapt_limit, interval.lower)
    if lower == FIRST_LINE_NUMBER:
        lower = None
    upper = map_optional(_adapt_limit, interval.upper)

    if lower is None:
        if upper is None:
            return intervals.Unlimited()
        else:
            return intervals.UpperLimit(upper)
    else:
        if upper is None:
            return intervals.LowerLimit(lower)
        else:
            if lower > upper:
                return intervals.Empty()
            else:
                return intervals.Finite(lower, upper)


def model_iter_from_file_line_iter(lines: Iterator[str]) -> Iterator[LineMatcherLine]:
    """
    Gives a sequence of line matcher models, corresponding to input lines read from file.
    New lines are expected to appear only as last character of lines, or not at all, if
    last line is not ended with new line in the file.

    @:param strings: lines from an input source
    """
    return enumerate((l.rstrip('\n') for l in lines),
                     FIRST_LINE_NUMBER)


def original_and_model_iter_from_file_line_iter(lines: Iterator[str]) -> Iterator[FullContentsAndLineMatcherLine]:
    """
    Gives a sequence of pairs, corresponding to each element in lines.
    (original line, line-matcher-model-for-line).

    See also docs of model_iter_from_file_line_iter.

    @:param strings: lines from an input source
    """
    return (
        _line_of(line_num, original)
        for line_num, original in enumerate(lines, FIRST_LINE_NUMBER)
    )


def original_and_model_iter_from_file_line_iter__interval(interval: IntInterval,
                                                          lines: Iterator[str],
                                                          ) -> Iterator[FullContentsAndLineMatcherLine]:
    """
    Gives a sequence of pairs, corresponding to each element in lines.
    (original line, line-matcher-model-for-line).

    See also docs of model_iter_from_file_line_iter.

    :param interval: Must be adapted to line number ranges. See func:`adapt_to_line_num_range`
    :param lines: lines from an input source
    """
    if interval.is_empty:
        return iter(())
    if interval.lower is None and interval.upper is None:
        return original_and_model_iter_from_file_line_iter(lines)

    num_to_skip = (
        0
        if interval.lower is None
        else
        interval.lower - 1
    )
    is_after_last = (
        _is_last__never
        if interval.upper is None
        else
        lambda ln: ln == interval.upper
    )

    return _lines_interval(num_to_skip, is_after_last, lines)


def _lines_interval(num_to_skip: int,
                    is_last_line_num: Callable[[int], bool],
                    lines: Iterator[str],
                    ) -> Iterator[FullContentsAndLineMatcherLine]:
    ln = 0

    if num_to_skip > 0:
        for _ in lines:
            ln += 1
            if ln == num_to_skip:
                break

    for line in lines:
        ln += 1
        yield _line_of(ln, line)
        if is_last_line_num(ln):
            return


def _line_of(n: int, full_line: str) -> FullContentsAndLineMatcherLine:
    return full_line, (n, full_line.rstrip('\n'))


def _is_last__never(ln: int) -> bool:
    return False


def _adapt_limit(limit: int) -> int:
    return max(FIRST_LINE_NUMBER, limit)
