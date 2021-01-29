from typing import Sequence, List, Callable

from exactly_lib.impls.types.string_transformer.impl.filter.line_nums import range_merge
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from . import sources
from .range_expr import Range, RangeVisitor, \
    LowerAndUpperLimitRange, UpperLimitRange, LowerLimitRange, \
    SingleLineRange


class SingleLineRangeTransformer(StringTransformer):
    def __init__(self,
                 name: str,
                 get_structure: Callable[[], StructureRenderer],
                 range_: Range,
                 mem_buff_size: int,
                 ):
        self._name = name
        self._range = range_
        self._get_structure = get_structure
        self._mem_buff_size = mem_buff_size

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._get_structure()

    def transform(self, model: StringSource) -> StringSource:
        model_constructor = _SingleRangeSourceConstructor(model, self._get_structure, self._mem_buff_size)
        return self._range.accept(model_constructor)


class MultipleLineRangesTransformer(StringTransformer):
    def __init__(self,
                 name: str,
                 get_structure: Callable[[], StructureRenderer],
                 ranges: Sequence[Range],
                 mem_buff_size: int,
                 ):
        self._name = name
        self._get_structure = get_structure
        self._ranges = ranges
        self._mem_buff_size = mem_buff_size

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._get_structure()

    def transform(self, model: StringSource) -> StringSource:
        output_of_non_neg_values = range_merge.Partitioning([], [], [])
        negatives = range_merge.partition(self._ranges, output_of_non_neg_values)
        return (
            self._model_for_negatives(model, negatives, output_of_non_neg_values)
            if negatives
            else
            self._model_for_non_negatives(model, output_of_non_neg_values)
        )

    def _model_for_non_negatives(self,
                                 model: StringSource,
                                 non_neg_values: range_merge.Partitioning,
                                 ) -> StringSource:
        merged_ranges = range_merge.merge(non_neg_values)

        if merged_ranges.is_empty:
            return sources.empty(model,
                                 self._get_structure)
        elif merged_ranges.is_everything():
            return model
        else:
            return sources.segments_source(
                self._mem_buff_size,
                self._get_structure,
                model,
                sources.SegmentsWithPositiveIncreasingValues(
                    merged_ranges.head,
                    merged_ranges.body,
                    merged_ranges.tail,
                )
            )

    def _model_for_negatives(self,
                             model: StringSource,
                             negatives: List[Range],
                             output_of_non_neg_values: range_merge.Partitioning,
                             ) -> StringSource:
        return sources.multiple_ranges_w_negative_values(
            self._mem_buff_size,
            self._get_structure,
            model,
            negatives,
            output_of_non_neg_values
        )


class _SingleRangeSourceConstructor(RangeVisitor[StringSource]):
    def __init__(self,
                 source_model: StringSource,
                 transformer_description: Callable[[], StructureRenderer],
                 mem_buff_size: int,
                 ):
        self._source_model = source_model
        self._transformer_description = transformer_description
        self._mem_buff_size = mem_buff_size

    def visit_single_line(self, x: SingleLineRange) -> StringSource:
        line_num = x.line_number
        if line_num == 0:
            return sources.empty(self._source_model,
                                 self._transformer_description)
        elif line_num > 0:
            return sources.single_non_neg_int_source(self._mem_buff_size, self._transformer_description,
                                                     self._source_model, line_num - 1)
        else:
            return sources.single_neg_int_source(self._mem_buff_size, self._transformer_description,
                                                 self._source_model, line_num)

    def visit_upper_limit(self, x: UpperLimitRange) -> StringSource:
        limit = x.upper_limit

        if limit == 0:
            return sources.empty(self._source_model,
                                 self._transformer_description)
        elif limit > 0:
            return sources.upper_non_neg_limit_source(self._mem_buff_size, self._transformer_description,
                                                      self._source_model, limit - 1)
        else:
            return sources.upper_neg_limit_source(self._mem_buff_size, self._transformer_description,
                                                  self._source_model, limit)

    def visit_lower_limit(self, x: LowerLimitRange) -> StringSource:
        limit = x.lower_limit

        if limit == 0:
            return sources.lower_non_neg_limit_source(self._mem_buff_size, self._transformer_description,
                                                      self._source_model, limit)
        elif limit > 0:
            return sources.lower_non_neg_limit_source(self._mem_buff_size, self._transformer_description,
                                                      self._source_model, limit - 1)
        else:
            return sources.lower_neg_limit_source(self._mem_buff_size, self._transformer_description,
                                                  self._source_model, limit)

    def visit_lower_and_upper_limit(self, x: LowerAndUpperLimitRange) -> StringSource:
        lower = x.lower_limit
        upper = x.upper_limit
        if upper == 0:
            return sources.empty(self._source_model,
                                 self._transformer_description)

        if lower >= 0:
            if upper >= 0:
                return self._lower_and_upper__non_neg(lower, upper)
            else:
                return self._lower_non_neg__upper_neg(lower, upper)
        else:
            if upper >= 0:
                return self._lower_neg__upper_non_neg(lower, upper)
            else:
                return self._lower_and_upper__neg(lower, upper)

    def _lower_and_upper__non_neg(self, lower: int, upper: int) -> StringSource:
        if lower > upper:
            return sources.empty(self._source_model,
                                 self._transformer_description)

        if lower > 0:
            lower -= 1
        upper -= 1

        return sources.lower_non_neg_upper_non_neg_source(self._mem_buff_size, self._transformer_description,
                                                          self._source_model, lower, upper)

    def _lower_and_upper__neg(self, lower: int, upper: int) -> StringSource:
        return (
            sources.empty(self._source_model,
                          self._transformer_description)
            if lower > upper
            else
            sources.lower_neg_upper_neg_source(self._mem_buff_size, self._transformer_description,
                                               self._source_model, lower, upper)
        )

    def _lower_non_neg__upper_neg(self, lower: int, upper: int) -> StringSource:
        if lower > 0:
            lower -= 1
        return sources.lower_non_neg_upper_neg_source(self._mem_buff_size, self._transformer_description,
                                                      self._source_model, lower, upper)

    def _lower_neg__upper_non_neg(self, lower: int, upper: int) -> StringSource:
        if upper > 0:
            upper -= 1
        return sources.lower_neg_upper_non_neg_source(self._mem_buff_size, self._transformer_description,
                                                      self._source_model, lower, upper)
