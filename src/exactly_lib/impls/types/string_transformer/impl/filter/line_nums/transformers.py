from typing import Sequence, List

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
                 range_: Range,
                 structure: StructureRenderer,
                 ):
        self._name = name
        self._range = range_
        self._structure = structure

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._structure

    def transform(self, model: StringSource) -> StringSource:
        model_constructor = _SingleRangeSourceConstructor(model)
        return self._range.accept(model_constructor)


class MultipleLineRangesTransformer(StringTransformer):
    def __init__(self,
                 name: str,
                 ranges: Sequence[Range],
                 structure: StructureRenderer,
                 ):
        self._ranges = ranges
        self._name = name
        self._structure = structure

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._structure

    def transform(self, model: StringSource) -> StringSource:
        output_of_non_neg_values = range_merge.Partitioning([], [], [])
        negatives = range_merge.partition(self._ranges, output_of_non_neg_values)
        return (
            self._model_for_negatives(model, negatives, output_of_non_neg_values)
            if negatives
            else
            self._model_for_non_negatives(model, output_of_non_neg_values)
        )

    @staticmethod
    def _model_for_non_negatives(model: StringSource,
                                 non_neg_values: range_merge.Partitioning,
                                 ) -> StringSource:
        merged_ranges = range_merge.merge(non_neg_values)

        if merged_ranges.is_empty:
            return sources.Empty(model)
        elif merged_ranges.is_everything():
            return model
        else:
            return sources.SegmentsSource(
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
        return sources.MultipleRangesWNegativeValues(
            model,
            negatives,
            output_of_non_neg_values
        )


class _SingleRangeSourceConstructor(RangeVisitor[StringSource]):
    def __init__(self, source_model: StringSource):
        self._source_model = source_model

    def visit_single_line(self, x: SingleLineRange) -> StringSource:
        line_num = x.line_number
        if line_num == 0:
            return sources.Empty(self._source_model)
        elif line_num > 0:
            return sources.SingleNonNegIntSource(self._source_model, line_num - 1)
        else:
            return sources.SingleNegIntSource(self._source_model, line_num)

    def visit_upper_limit(self, x: UpperLimitRange) -> StringSource:
        limit = x.upper_limit

        if limit == 0:
            return sources.Empty(self._source_model)
        elif limit > 0:
            return sources.UpperNonNegLimitSource(self._source_model, limit - 1)
        else:
            return sources.UpperNegLimitSource(self._source_model, limit)

    def visit_lower_limit(self, x: LowerLimitRange) -> StringSource:
        limit = x.lower_limit

        if limit == 0:
            return sources.LowerNonNegLimitSource(self._source_model, limit)
        elif limit > 0:
            return sources.LowerNonNegLimitSource(self._source_model, limit - 1)
        else:
            return sources.LowerNegLimitSource(self._source_model, limit)

    def visit_lower_and_upper_limit(self, x: LowerAndUpperLimitRange) -> StringSource:
        lower = x.lower_limit
        upper = x.upper_limit
        if upper == 0:
            return sources.Empty(self._source_model)

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
            return sources.Empty(self._source_model)

        if lower > 0:
            lower -= 1
        upper -= 1

        return sources.LowerNonNegUpperNonNegSource(self._source_model, lower, upper)

    def _lower_and_upper__neg(self, lower: int, upper: int) -> StringSource:
        return (
            sources.Empty(self._source_model)
            if lower > upper
            else
            sources.LowerNegUpperNegSource(self._source_model, lower, upper)
        )

    def _lower_non_neg__upper_neg(self, lower: int, upper: int) -> StringSource:
        if lower > 0:
            lower -= 1
        return sources.LowerNonNegUpperNegSource(self._source_model, lower, upper)

    def _lower_neg__upper_non_neg(self, lower: int, upper: int) -> StringSource:
        if upper > 0:
            upper -= 1
        return sources.LowerNegUpperNonNegSource(self._source_model, lower, upper)
