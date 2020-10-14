from typing import Optional, Sequence, List

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.integer import validation as int_validation
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.validation_error_exception import ValidationErrorException
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv, \
    StringTransformerAdv
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable
from . import models
from . import range_expr
from .range_expr import Range, RangeVisitor, LowerAndUpperLimitRange, UpperLimitRange, LowerLimitRange, \
    SingleLineRange
from ... import names


def sdv(name: str, range_expr_: StringSdv) -> StringTransformerSdv:
    range_expr_handler = _RangeExprHandler(range_expr_)

    def make_ddv(symbols: SymbolTable) -> StringTransformerDdv:
        range_expr_handler.resolve(symbols)
        return _LineNumRangeTransformerDdv(name, range_expr_handler)

    return sdvs.SdvFromParts(
        make_ddv,
        range_expr_handler.references(),
    )


class _RangeExprHandler:
    """
    Takes care of the (unfortunate) fact that resolving happens multiple times.

    This behaviour should be changed in the future.
    """

    def __init__(self, range_expr_sdv: StringSdv):
        self._sdv = range_expr_sdv
        self.range_expr_str = None
        self.validator = None

    def references(self) -> Sequence[SymbolReference]:
        return self._sdv.references

    def resolve(self, symbols: SymbolTable):
        if self.range_expr_str is None:
            self.range_expr_str = self._sdv.resolve(symbols).value_when_no_dir_dependencies()
            self.validator = _RangeValidator(self.range_expr_str)


class _LineNumRangeTransformerDdv(StringTransformerDdv):
    def __init__(self,
                 name: str,
                 range_expr_handler: _RangeExprHandler,
                 ):
        self._name = name
        self._range_expr_handler = range_expr_handler

    def structure(self) -> StructureRenderer:
        return _LineNumRangeTransformer.new_structure_tree(
            self._name,
            self._range_expr_handler.range_expr_str,
        )

    @property
    def validator(self) -> DdvValidator:
        return self._range_expr_handler.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return advs.ConstantAdv(
            _LineNumRangeTransformer(self._name,
                                     self._range_expr_handler.validator.range_after_validation)
        )


class _RangeValidator(DdvValidator):
    def __init__(self, range_expr: str):
        self._range_expr = range_expr
        self.range_after_validation = None

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        if self.range_after_validation is not None:
            return None

        parser = _RangeParser(self._range_expr)
        try:
            self.range_after_validation = parser.parse()
        except ValidationErrorException as ex:
            return ex.error

        return None

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        return None

    def validate_pre_or_post_sds(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        return self.validate_pre_sds_if_applicable(tcds.hds)


class _RangeParser:
    def __init__(self, range_expr_str: str):
        self._range_expr = range_expr_str

    def parse(self) -> Range:
        limit_parts = self._split_into_valid_number_of_parts()

        num_parts = len(limit_parts)

        if num_parts == 1:
            return self._single_int_range(limit_parts[0])
        else:
            if not limit_parts[0]:
                return self._upper_limit_range(limit_parts[1])
            elif not limit_parts[1]:
                return self._lower_limit_range(limit_parts[0])
            else:
                return self._lower_and_upper_limit_range(limit_parts[0], limit_parts[1])

    def _split_into_valid_number_of_parts(self) -> List[str]:
        self._range_expr_must_not_be_empty()

        limit_parts = self._range_expr.strip().split(names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR)

        if len(limit_parts) > 2:
            msg = text_docs.single_pre_formatted_line_object(
                str_constructor.FormatPositional(
                    'Invalid {} (found more than one "{}"): {}',
                    names.RANGE_EXPR_SED_NAME,
                    names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR,
                    repr(self._range_expr))
            )
            raise ValidationErrorException(msg)

        return limit_parts

    def _range_expr_must_not_be_empty(self):
        if self._range_expr == '' or self._range_expr.isspace():
            msg = text_docs.single_pre_formatted_line_object(
                str_constructor.FormatPositional(
                    'Empty {}: {}',
                    names.RANGE_EXPR_SED_NAME,
                    repr(self._range_expr))
            )
            raise ValidationErrorException(msg)

    @staticmethod
    def _single_int_range(int_expr: str) -> Range:
        return range_expr.SingleLineRange(
            int_validation.evaluate(int_expr)
        )

    @staticmethod
    def _lower_limit_range(int_expr: str) -> Range:
        return range_expr.LowerLimitRange(
            int_validation.evaluate(int_expr)
        )

    @staticmethod
    def _upper_limit_range(int_expr: str) -> Range:
        return range_expr.UpperLimitRange(
            int_validation.evaluate(int_expr)
        )

    @staticmethod
    def _lower_and_upper_limit_range(lower: str, upper: str) -> Range:
        return range_expr.LowerAndUpperLimitRange(
            int_validation.evaluate(lower),
            int_validation.evaluate(upper),
        )


class _LineNumRangeTransformer(StringTransformer):
    def __init__(self,
                 name: str,
                 range_expr_: Range,
                 ):
        self._name = name
        self._range_expr = range_expr_
        self._range_expr_str = str(range_expr_)
        range_presentation_str = range_expr_.accept(_RangePresenter())
        self._structure = self.new_structure_tree(name, range_presentation_str)

    @staticmethod
    def new_structure_tree(name: str,
                           range_expr_: str) -> StructureRenderer:
        if range_expr_ == '' or range_expr_.isspace():
            range_expr_ = repr(range_expr_)

        return renderers.NodeRendererFromParts(
            name,
            None,
            (details.String(range_expr_),),
            (),
        )

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._structure

    def transform(self, model: StringModel) -> StringModel:
        model_constructor = _ModelConstructor(model)
        return self._range_expr.accept(model_constructor)


class _ModelConstructor(RangeVisitor[StringModel]):
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


class _RangePresenter(RangeVisitor[str]):
    def visit_single_line(self, x: SingleLineRange) -> str:
        return str(x.line_number)

    def visit_upper_limit(self, x: UpperLimitRange) -> str:
        return names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR + str(x.upper_limit)

    def visit_lower_limit(self, x: LowerLimitRange) -> str:
        return str(x.lower_limit) + names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR

    def visit_lower_and_upper_limit(self, x: LowerAndUpperLimitRange) -> str:
        return names.LINE_NUMBERS_FILTER__LIMIT_SEPARATOR.join((str(x.lower_limit),
                                                                str(x.upper_limit)))
