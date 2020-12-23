from typing import Optional, List, Sequence

from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import LowerAndUpperLimitRange, \
    Range, RangeVisitor, UpperLimitRange, LowerLimitRange, \
    SingleLineRange, FromTo
from exactly_lib.type_val_prims.matcher.line_matcher import FIRST_LINE_NUMBER


class MergedRanges:
    def __init__(self,
                 head: Optional[int],
                 body: List[FromTo],
                 tail: Optional[int],
                 is_empty: bool,
                 ):
        """
        :param head: if present as n: the ranges include (neg infinity, n]
        :param body:
        :param tail: if present as n: the ranges include [n, pos infinity)
        :param is_empty:
        """
        self.head = head
        self.body = body
        self.tail = tail
        self.is_empty = is_empty

    @staticmethod
    def empty() -> 'MergedRanges':
        return MergedRanges(None, [], None, True)

    @staticmethod
    def everything() -> 'MergedRanges':
        return MergedRanges(None, [], None, False)

    def is_everything(self) -> bool:
        return (
                not self.is_empty and
                self.head is None and
                self.tail is None and
                not self.body
        )


class Partitioning:
    def __init__(self,
                 head: List[int],
                 segments: List[FromTo],
                 tail: List[int],
                 ):
        """
        :param segments: No segment starts from FIRST_LINE_NUMBER
        Such segments should be represented via head.
        """
        self.head_to = head
        self.segments = segments
        self.tail_from = tail


def partition(ranges: Sequence[Range],
              output_of_non_neg_values: Partitioning,
              ) -> List[Range]:
    """
    :param ranges: Ranges to partition
    :param output_of_non_neg_values: ranges w non-neg values are put in this object
    :return: ranges w negative values
    """
    partitioner = _Partitioner(output_of_non_neg_values)
    ranges_w_neg_value = []
    for range_ in ranges:
        mb_negative_range = range_.accept(partitioner)
        if mb_negative_range:
            ranges_w_neg_value.append(mb_negative_range)

    return ranges_w_neg_value


def translate_neg_to_non_neg(ranges: List[Range],
                             num_model_lines: int) -> List[Range]:
    ret_val = []
    translator = _NegValuesTranslator(num_model_lines)

    for range_ in ranges:
        ret_val.append(range_.accept(translator))

    return ret_val


def merge(partitioning: Partitioning) -> MergedRanges:
    segments_to_process = sorted(filter(_is_valid_segment, partitioning.segments))

    head_to = (
        None
        if not partitioning.head_to
        else
        max(partitioning.head_to)
    )

    tail_from = (
        None
        if not partitioning.tail_from
        else
        min(partitioning.tail_from)
    )

    if not segments_to_process:
        if head_to is None and tail_from is None:
            return MergedRanges.empty()

    if segments_to_process:
        segments_to_process = _merge_segments(segments_to_process)

    non_merged_segments_output = []

    if head_to is not None:
        head_to = _merge_head_to(head_to, segments_to_process, non_merged_segments_output)
        segments_to_process = non_merged_segments_output
        non_merged_segments_output = []

    if tail_from is not None:
        tail_from = _merge_tail_from(tail_from, segments_to_process, non_merged_segments_output)
        segments_to_process = non_merged_segments_output

    if tail_from is not None:
        if tail_from == 1:
            return MergedRanges.everything()
        if head_to is not None and head_to + 1 >= tail_from:
            return MergedRanges.everything()

    if head_to is None and segments_to_process:
        first_segment = segments_to_process[0]
        if first_segment[0] == FIRST_LINE_NUMBER:
            head_to = first_segment[1]
            del segments_to_process[0]

    return MergedRanges(head_to, segments_to_process, tail_from, False)


def _is_valid_segment(x: FromTo) -> bool:
    return x[0] <= x[1]


def _merge_segments(segments: List[FromTo]) -> List[FromTo]:
    ret_val = []

    current = segments[0]
    for next_ in segments[1:]:
        if _can_be_one(current, next_):
            current = (current[0],
                       max(current[1], next_[1]))
        else:
            ret_val.append(current)
            current = next_

    ret_val.append(current)
    return ret_val


def _can_be_one(first: FromTo, second: FromTo) -> bool:
    return first[1] + 1 >= second[0]


def _merge_head_to(initial: int,
                   segments: List[FromTo],
                   non_merged__out__sorted: List[FromTo],
                   ) -> int:
    for from_to in segments:
        if from_to[0] <= initial + 1:
            initial = max(initial, from_to[1])
        else:
            non_merged__out__sorted.append(from_to)

    return initial


def _merge_tail_from(initial: int,
                     segments: List[FromTo],
                     non_merged__out__sorted: List[FromTo],
                     ) -> int:
    for from_to in reversed(segments):
        if from_to[1] >= initial - 1:
            initial = min(initial, from_to[0])
        else:
            non_merged__out__sorted.insert(0, from_to)

    return initial


class _Partitioner(RangeVisitor[Optional[Range]]):
    """
    Store ranges w non-neg values in the output.
    Ranges w neg values are returned.
    """

    def __init__(self, output: Partitioning):
        self._o = output

    def visit_single_line(self, x: SingleLineRange) -> Optional[Range]:
        n = x.line_number

        if n < 0:
            return x
        if n != 0:
            self._o.segments.append((n, n))

    def visit_lower_limit(self, x: LowerLimitRange) -> Optional[Range]:
        if x.lower_limit < 0:
            return x
        self._o.tail_from.append(max(1, x.lower_limit))

    def visit_upper_limit(self, x: UpperLimitRange) -> Optional[Range]:
        n = x.upper_limit

        if n < 0:
            return x
        if n != 0:
            self._o.head_to.append(n)

    def visit_lower_and_upper_limit(self, x: LowerAndUpperLimitRange) -> Optional[Range]:
        if x.lower_limit < 0 or x.upper_limit < 0:
            return x

        if x.upper_limit != 0:
            if x.lower_limit <= FIRST_LINE_NUMBER:
                self._o.head_to.append(x.upper_limit)
            else:
                self._o.segments.append((x.lower_limit, x.upper_limit))


class _NegValuesTranslator(RangeVisitor[Range]):
    """
    Store ranges w non-neg values in the output.
    Ranges w neg values are returned.
    """

    def __init__(self, num_lines: int):
        self._num_lines = num_lines

    def _tr(self, n: int) -> int:
        return (
            n
            if n >= 0
            else
            max(0, self._num_lines + n + 1)
        )

    def visit_single_line(self, x: SingleLineRange) -> Range:
        return SingleLineRange(self._tr(x.line_number))

    def visit_lower_limit(self, x: LowerLimitRange) -> Range:
        return LowerLimitRange(self._tr(x.lower_limit))

    def visit_upper_limit(self, x: UpperLimitRange) -> Range:
        return UpperLimitRange(self._tr(x.upper_limit))

    def visit_lower_and_upper_limit(self, x: LowerAndUpperLimitRange) -> Range:
        return LowerAndUpperLimitRange(self._tr(x.lower_limit),
                                       self._tr(x.upper_limit))
