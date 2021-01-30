from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from typing import Iterator, List, Optional, Deque, Callable, ContextManager

from exactly_lib.impls.types.string_source.cached_frozen import StringSourceWithCachedFrozen
from exactly_lib.impls.types.string_source.contents import delegated_with_init
from exactly_lib.impls.types.string_source.source_from_contents import StringSourceWConstantContents
from exactly_lib.impls.types.string_source.source_from_lines import StringSourceContentsFromLinesBase
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums import range_merge
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import FromTo, Range
from exactly_lib.impls.types.string_transformer.impl.filter.string_sources import \
    TransformedContentsViaAsLinesBase
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


def empty(transformed: StringSource,
          transformer_description: Callable[[], StructureRenderer],
          ) -> StringSource:
    def new_structure_builder() -> StringSourceStructureBuilder:
        return transformed.new_structure_builder().with_transformed_by(transformer_description())

    return StringSourceWConstantContents(
        new_structure_builder,
        _EmptyContents(transformed),
    )


def single_non_neg_int_source(mem_buff_size: int,
                              transformer_description: Callable[[], StructureRenderer],
                              source: StringSource,
                              zero_based_line_num: int,
                              ) -> StringSource:
    return _string_source_of_lines_transformer(
        _SingleNonNegIntTransformer(zero_based_line_num),
        transformer_description,
        source,
        mem_buff_size,
    )


def single_neg_int_source(mem_buff_size: int,
                          transformer_description: Callable[[], StructureRenderer],
                          source: StringSource,
                          neg_line_num: int,
                          ) -> StringSource:
    return _string_source_of_lines_transformer(
        _SingleNegIntTransformer(neg_line_num),
        transformer_description,
        source,
        mem_buff_size,
    )


def upper_non_neg_limit_source(mem_buff_size: int,
                               transformer_description: Callable[[], StructureRenderer],
                               source: StringSource,
                               zero_based_upper_limit: int,
                               ) -> StringSource:
    return _string_source_of_lines_transformer(
        _UpperNonNegLimitTransformer(zero_based_upper_limit),
        transformer_description,
        source,
        mem_buff_size,
    )


def upper_neg_limit_source(mem_buff_size: int,
                           transformer_description: Callable[[], StructureRenderer],
                           source: StringSource,
                           neg_line_num: int,
                           ) -> StringSource:
    return _string_source_of_lines_transformer(
        _UpperNegLimitTransformer(neg_line_num),
        transformer_description,
        source,
        mem_buff_size,
    )


def lower_non_neg_limit_source(mem_buff_size: int,
                               transformer_description: Callable[[], StructureRenderer],
                               source: StringSource,
                               zero_based_lower_limit: int,
                               ) -> StringSource:
    return _string_source_of_lines_transformer(
        _LowerNonNegLimitTransformer(zero_based_lower_limit),
        transformer_description,
        source,
        mem_buff_size,
    )


def lower_neg_limit_source(mem_buff_size: int,
                           transformer_description: Callable[[], StructureRenderer],
                           source: StringSource,
                           neg_line_num: int,
                           ) -> StringSource:
    return _string_source_of_lines_transformer(
        _LowerNegLimitTransformer(neg_line_num),
        transformer_description,
        source,
        mem_buff_size,
    )


def lower_non_neg_upper_non_neg_source(mem_buff_size: int,
                                       transformer_description: Callable[[], StructureRenderer],
                                       source: StringSource,
                                       zero_based_lower_limit: int,
                                       zero_based_upper_limit: int,
                                       ) -> StringSource:
    return _string_source_of_lines_transformer(
        _LowerNonNegUpperNonNegTransformer(zero_based_lower_limit, zero_based_upper_limit),
        transformer_description,
        source,
        mem_buff_size,
    )


def lower_non_neg_upper_neg_source(mem_buff_size: int,
                                   transformer_description: Callable[[], StructureRenderer],
                                   source: StringSource,
                                   zero_based_lower_limit: int,
                                   neg_upper_limit: int,
                                   ) -> StringSource:
    return _string_source_of_lines_transformer(
        _LowerNonNegUpperNegTransformer(zero_based_lower_limit, neg_upper_limit),
        transformer_description,
        source,
        mem_buff_size,
    )


def lower_neg_upper_non_neg_source(mem_buff_size: int,
                                   transformer_description: Callable[[], StructureRenderer],
                                   source: StringSource,
                                   neg_lower_limit: int,
                                   zero_based_upper_limit: int,
                                   ) -> StringSource:
    return _string_source_of_lines_transformer(
        _LowerNegUpperNonNegTransformer(neg_lower_limit, zero_based_upper_limit),
        transformer_description,
        source,
        mem_buff_size,
    )


def lower_neg_upper_neg_source(mem_buff_size: int,
                               transformer_description: Callable[[], StructureRenderer],
                               source: StringSource,
                               neg_lower_limit: int,
                               neg_upper_limit: int,
                               ) -> StringSource:
    return _string_source_of_lines_transformer(
        _LowerNegUpperNegTransformer(neg_lower_limit, neg_upper_limit),
        transformer_description,
        source,
        mem_buff_size,
    )


class SegmentsWithPositiveIncreasingValues:
    def __init__(self,
                 head: Optional[int],
                 body: List[FromTo],
                 tail: Optional[int],
                 ):
        self.head = head
        self.body = body
        self.tail = tail


def segments_source(mem_buff_size: int,
                    transformer_description: Callable[[], StructureRenderer],
                    source: StringSource,
                    segments: SegmentsWithPositiveIncreasingValues,
                    ) -> StringSource:
    return _string_source_of_lines_transformer(
        _TransformMethodOfSegments(segments),
        transformer_description,
        source,
        mem_buff_size,
    )


def multiple_ranges_w_negative_values(
        mem_buff_size: int,
        transformer_description: Callable[[], StructureRenderer],
        source: StringSource,
        negatives: List[Range],
        partial_partitioning: range_merge.Partitioning,
) -> StringSource:
    def new_structure_builder() -> StringSourceStructureBuilder:
        return source.new_structure_builder().with_transformed_by(transformer_description())

    def may_depend_on_external_resources_of_uninitialized() -> bool:
        return source.contents().may_depend_on_external_resources

    def get_tmp_file_space() -> DirFileSpace:
        return source.contents().tmp_file_space

    return StringSourceWithCachedFrozen(
        new_structure_builder,
        delegated_with_init.DelegatedStringSourceContentsWithInit(
            _HandlerResolverForMultipleRangesWNegativeValues(source, negatives, partial_partitioning).resolve,
            may_depend_on_external_resources_of_uninitialized,
            get_tmp_file_space,
        ),
        mem_buff_size,
        None,
    )


class _EmptyContents(StringSourceContentsFromLinesBase):
    def __init__(self, transformed: StringSource):
        super().__init__()
        self._transformed = transformed

    @property
    def may_depend_on_external_resources(self) -> bool:
        return False

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(())

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._transformed.contents().tmp_file_space


class _LinesTransformer(ABC):
    @abstractmethod
    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        pass


def _string_source_of_lines_transformer(
        transformer: _LinesTransformer,
        transformer_description: Callable[[], StructureRenderer],
        source: StringSource,
        mem_buff_size: int,
) -> StringSource:
    def new_structure_builder() -> StringSourceStructureBuilder:
        return source.new_structure_builder().with_transformed_by(transformer_description())

    return StringSourceWithCachedFrozen(
        new_structure_builder,
        _ContentsOfLinesTransformer(transformer, source),
        mem_buff_size,
        None,
    )


class _ContentsOfLinesTransformer(TransformedContentsViaAsLinesBase):
    def __init__(self,
                 transformer: _LinesTransformer,
                 source: StringSource,
                 ):
        super().__init__(source, None)
        self._transformer = transformer

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._source.contents().may_depend_on_external_resources

    def _transform_lines(self, lines: Iterator[str]) -> Iterator[str]:
        return self._transformer.transform(lines)


class _SingleNonNegIntTransformer(_LinesTransformer):
    def __init__(self, zero_based_line_num: int):
        self._zero_based_line_num = zero_based_line_num

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        requested = self._zero_based_line_num
        current = 0
        for line in lines:
            if requested == current:
                yield line
                break
            else:
                current += 1


class _SingleNegIntTransformer(_LinesTransformer):
    def __init__(self, neg_line_num: int):
        self._neg_line_num = neg_line_num
        self._pocket_size = abs(neg_line_num)

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        pocket = _filled_pocket(self._pocket_size, lines)

        if len(pocket) < self._pocket_size:
            return

        for next_line in lines:
            pocket.popleft()
            pocket.append(next_line)

        yield pocket[0]


class _UpperNonNegLimitTransformer(_LinesTransformer):
    def __init__(self, zero_based_upper_limit: int):
        self._zero_based_upper_limit = zero_based_upper_limit

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        limit = self._zero_based_upper_limit
        current = 0

        for line in lines:
            yield line
            if limit == current:
                return
            current += 1


class _UpperNegLimitTransformer(_LinesTransformer):
    def __init__(self, neg_line_num: int):
        self._neg_line_num = neg_line_num

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        pocket_size = abs(self._neg_line_num)
        pocket = _filled_pocket(pocket_size, lines)

        if len(pocket) < pocket_size:
            return

        yield pocket[0]

        for next_line in lines:
            pocket.popleft()
            pocket.append(next_line)

            yield pocket[0]


class _LowerNonNegLimitTransformer(_LinesTransformer):
    def __init__(self, zero_based_lower_limit: int):
        self._zero_based_lower_limit = zero_based_lower_limit

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        _skip(self._zero_based_lower_limit, lines)

        for line in lines:
            yield line


class _LowerNegLimitTransformer(_LinesTransformer):
    def __init__(self, neg_line_num: int):
        self._neg_line_num = neg_line_num

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        pocket_size = abs(self._neg_line_num)
        pocket = _filled_pocket(pocket_size, lines)

        for next_line in lines:
            pocket.popleft()
            pocket.append(next_line)

        for line in pocket:
            yield line


class _LowerNonNegUpperNonNegTransformer(_LinesTransformer):
    def __init__(self,
                 zero_based_lower_limit: int,
                 zero_based_upper_limit: int,
                 ):
        self._zero_based_lower_limit = zero_based_lower_limit
        self._zero_based_upper_limit = zero_based_upper_limit

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        _skip(self._zero_based_lower_limit, lines)
        num_requested = self._zero_based_upper_limit - self._zero_based_lower_limit + 1

        for line in _limited(lines, num_requested):
            yield line


class _LowerNonNegUpperNegTransformer(_LinesTransformer):
    def __init__(self,
                 zero_based_lower_limit: int,
                 neg_upper_limit: int,
                 ):
        self._zero_based_lower_limit = zero_based_lower_limit
        self._neg_upper_limit = neg_upper_limit

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        upper_len = abs(self._neg_upper_limit)

        pocket = _filled_pocket(upper_len, lines)

        if len(pocket) < upper_len:
            return

        if not self._forward_pocket_to_lower_limit(pocket, lines):
            return

        yield pocket[0]
        for line in lines:
            pocket.popleft()
            pocket.append(line)
            yield pocket[0]

    def _forward_pocket_to_lower_limit(self, pocket: Deque[str], lines: Iterator[str]) -> bool:
        left_to_consume = self._zero_based_lower_limit

        for next_line in _limited(lines, left_to_consume):
            pocket.popleft()
            pocket.append(next_line)
            left_to_consume -= 1

        return left_to_consume == 0


class _LowerNegUpperNonNegTransformer(_LinesTransformer):
    def __init__(self,
                 neg_lower_limit: int,
                 zero_based_upper_limit: int,
                 ):
        self._neg_lower_limit = neg_lower_limit
        self._zero_based_upper_limit = zero_based_upper_limit

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        upper = self._zero_based_upper_limit
        lower_len = abs(self._neg_lower_limit)

        pocket = _filled_pocket(lower_len, lines)

        pocket_1st_idx = 0
        for line in lines:
            pocket.popleft()
            pocket.append(line)

            pocket_1st_idx += 1
            if pocket_1st_idx > upper:
                return

        num_to_produce = upper - pocket_1st_idx + 1

        for line in pocket:
            if num_to_produce == 0:
                return
            yield line
            num_to_produce -= 1


class _LowerNegUpperNegTransformer(_LinesTransformer):
    def __init__(self,
                 neg_lower_limit: int,
                 neg_upper_limit: int,
                 ):
        """
        neg_lower_limit < neg_upper_limit
        """
        self._neg_lower_limit = neg_lower_limit
        self._neg_upper_limit = neg_upper_limit

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        lower_len = abs(self._neg_lower_limit)
        upper_len = abs(self._neg_upper_limit)

        pocket = _filled_pocket(lower_len, lines)

        num_non_existing_at_head = lower_len - len(pocket)
        if num_non_existing_at_head != 0:
            lower_len -= num_non_existing_at_head
            if upper_len > lower_len:
                return

        for line in lines:
            del pocket[0]
            pocket.append(line)

        num_to_produce = lower_len - upper_len + 1

        for line in pocket:
            if num_to_produce == 0:
                return
            yield line
            num_to_produce -= 1


class _TransformMethodOfSegments(_LinesTransformer):
    def __init__(self, segments: SegmentsWithPositiveIncreasingValues):
        self._segments = segments

    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        segments = self._segments
        line_num = 0

        if segments.head is not None:
            end = segments.head
            for line in lines:
                line_num += 1
                yield line
                if line_num == end:
                    break

        for body_segment in segments.body:
            start_m1 = body_segment[0] - 1
            end = body_segment[1]

            for _ in lines:
                line_num += 1
                if line_num == start_m1:
                    break

            for line in lines:
                line_num += 1
                yield line
                if line_num == end:
                    break

        if segments.tail is not None:
            start_m1 = segments.tail - 1
            for _ in lines:
                line_num += 1
                if line_num == start_m1:
                    break

            for line in lines:
                yield line


class _EmptyLinesTransformer(_LinesTransformer):
    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        return ()


class _EverythingLinesTransformer(_LinesTransformer):
    def transform(self, lines: Iterator[str]) -> Iterator[str]:
        return lines


class _HandlerResolverForMultipleRangesWNegativeValues:
    def __init__(self,
                 source: StringSource,
                 negatives: List[Range],
                 partial_partitioning: range_merge.Partitioning,
                 ):
        self._source = source
        self._partial_partitioning = partial_partitioning
        self._negatives = negatives

    def resolve(self) -> StringSourceContents:
        self._source.freeze()

        num_lines = self._num_lines_of_source_model()
        merged_ranges = self._ranges_corresponding_to(num_lines)
        transformer = self._transform_method_for(merged_ranges)

        return _ContentsOfLinesTransformer(transformer, self._source)

    def _ranges_corresponding_to(self, num_lines: int) -> range_merge.MergedRanges:
        translated_negatives = range_merge.translate_neg_to_non_neg(self._negatives, num_lines)
        range_merge.partition(translated_negatives, self._partial_partitioning)
        return range_merge.merge(self._partial_partitioning)

    @staticmethod
    def _transform_method_for(merged_ranges: range_merge.MergedRanges) -> _LinesTransformer:
        if merged_ranges.is_empty:
            return _EmptyLinesTransformer()
        elif merged_ranges.is_everything():
            return _EverythingLinesTransformer()
        else:
            segments = SegmentsWithPositiveIncreasingValues(
                merged_ranges.head,
                merged_ranges.body,
                merged_ranges.tail,
            )

            return _TransformMethodOfSegments(segments)

    def _num_lines_of_source_model(self) -> int:
        n = 0

        with self._source.contents().as_lines as lines:
            for _ in lines:
                n += 1

        return n


def _limited(iterator: Iterator[str], size: int) -> Iterator[str]:
    if size == 0:
        return
    for e in iterator:
        yield e
        size -= 1
        if size == 0:
            return


def _skip(num_lines: int, lines: Iterator[str]):
    for _ in _limited(lines, num_lines):
        pass


def _filled_pocket(size: int, lines: Iterator[str]) -> Deque[str]:
    return deque(_limited(lines, size))
