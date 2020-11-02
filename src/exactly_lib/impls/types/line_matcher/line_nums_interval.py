from exactly_lib.impls.types.interval import matcher_interval
from exactly_lib.impls.types.line_matcher import model_construction
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher
from exactly_lib.util.interval.int_interval import IntInterval


def interval_of_matcher(matcher: LineMatcher) -> IntInterval:
    """
    Gives an interval, that covers all line numbers matched by matcher.

    The interval is adapted to the "line number range" (FIRST_LINE_NUMBER ...),
    for use with func:`model_construction.original_and_model_iter_from_file_line_iter__interval`.

    The purpose of the interval is to limit the lines needed to process for a given class:`LineMatcher`.
    Thereby gaining performance benefits and avoiding the need to process the tail of the input
    (if an upper limit can be derived).
    """
    return matcher_interval.interval_of(
        matcher,
        model_construction.LINES_INTERVAL_FOR_UNKNOWN_INTERVAL,
        model_construction.adapt_to_line_num_range,
    )
