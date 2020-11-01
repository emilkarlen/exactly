from typing import Sequence, List

from exactly_lib.test_case_utils.string_transformer.impl.filter.line_nums import range_merge
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from . import models
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

    def transform(self, model: StringModel) -> StringModel:
        model_constructor = _SingleRangeModelConstructor(model)
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

    def transform(self, model: StringModel) -> StringModel:
        output_of_non_neg_values = range_merge.Partitioning([], [], [])
        negatives = range_merge.partition(self._ranges, output_of_non_neg_values)
        return (
            self._model_for_negatives(model, negatives, output_of_non_neg_values)
            if negatives
            else
            self._model_for_non_negatives(model, output_of_non_neg_values)
        )

    @staticmethod
    def _model_for_non_negatives(model: StringModel,
                                 non_neg_values: range_merge.Partitioning,
                                 ) -> StringModel:
        merged_ranges = range_merge.merge(non_neg_values)

        if merged_ranges.is_empty:
            return models.Empty(model)
        elif merged_ranges.is_everything():
            return model
        else:
            return models.SegmentsModel(
                model,
                models.SegmentsWithPositiveIncreasingValues(
                    merged_ranges.head,
                    merged_ranges.body,
                    merged_ranges.tail,
                )
            )

    def _model_for_negatives(self,
                             model: StringModel,
                             negatives: List[Range],
                             output_of_non_neg_values: range_merge.Partitioning,
                             ) -> StringModel:
        return models.MultipleRangesWNegativeValues(
            model,
            negatives,
            output_of_non_neg_values
        )


class _SingleRangeModelConstructor(RangeVisitor[StringModel]):
    def __init__(self, source_model: StringModel):
        self._source_model = source_model

    def visit_single_line(self, x: SingleLineRange) -> StringModel:
        line_num = x.line_number
        if line_num == 0:
            return models.Empty(self._source_model)
        elif line_num > 0:
            return models.SingleNonNegIntModel(self._source_model, line_num - 1)
        else:
            return models.SingleNegIntModel(self._source_model, line_num)

    def visit_upper_limit(self, x: UpperLimitRange) -> StringModel:
        limit = x.upper_limit

        if limit == 0:
            return models.Empty(self._source_model)
        elif limit > 0:
            return models.UpperNonNegLimitModel(self._source_model, limit - 1)
        else:
            return models.UpperNegLimitModel(self._source_model, limit)

    def visit_lower_limit(self, x: LowerLimitRange) -> StringModel:
        limit = x.lower_limit

        if limit == 0:
            return models.LowerNonNegLimitModel(self._source_model, limit)
        elif limit > 0:
            return models.LowerNonNegLimitModel(self._source_model, limit - 1)
        else:
            return models.LowerNegLimitModel(self._source_model, limit)

    def visit_lower_and_upper_limit(self, x: LowerAndUpperLimitRange) -> StringModel:
        lower = x.lower_limit
        upper = x.upper_limit
        if upper == 0:
            return models.Empty(self._source_model)

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

    def _lower_and_upper__non_neg(self, lower: int, upper: int) -> StringModel:
        if lower > upper:
            return models.Empty(self._source_model)

        if lower > 0:
            lower -= 1
        upper -= 1

        return models.LowerNonNegUpperNonNegModel(self._source_model, lower, upper)

    def _lower_and_upper__neg(self, lower: int, upper: int) -> StringModel:
        return (
            models.Empty(self._source_model)
            if lower > upper
            else
            models.LowerNegUpperNegModel(self._source_model, lower, upper)
        )

    def _lower_non_neg__upper_neg(self, lower: int, upper: int) -> StringModel:
        if lower > 0:
            lower -= 1
        return models.LowerNonNegUpperNegModel(self._source_model, lower, upper)

    def _lower_neg__upper_non_neg(self, lower: int, upper: int) -> StringModel:
        if upper > 0:
            upper -= 1
        return models.LowerNegUpperNonNegModel(self._source_model, lower, upper)
