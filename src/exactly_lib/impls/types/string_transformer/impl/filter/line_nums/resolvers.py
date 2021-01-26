from typing import Optional, Sequence, List, Callable

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.exception.validation_error_exception import ValidationErrorException
from exactly_lib.impls.types.integer import validation as int_validation
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer import sdvs
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums import range_expr
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import Range
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util import collection
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.str_.str_constructor import ToStringObject
from exactly_lib.util.symbol_table import SymbolTable
from . import transformers


def sdv(name: str, range_expr_s: Sequence[StringSdv]) -> StringTransformerSdv:
    range_expr_handlers = [
        _RangeExprHandler(re)
        for re in range_expr_s
    ]
    references = collection.concat_list([s.references for s in range_expr_s])

    def make_ddv(symbols: SymbolTable) -> StringTransformerDdv:
        for range_expr_handler in range_expr_handlers:
            range_expr_handler.resolve(symbols)

        return _LineNumRangeTransformerDdv(name, range_expr_handlers)

    return sdvs.SdvFromParts(
        make_ddv,
        references,
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
                 range_expr_handlers: Sequence[_RangeExprHandler],
                 ):
        self._name = name
        self._range_expr_handlers = range_expr_handlers
        self._validator = ddv_validators.all_of([
            reh.validator
            for reh in range_expr_handlers
        ])

    def structure(self) -> StructureRenderer:
        return _StructureRenderer(self._name, [
            reh.range_expr_str
            for reh in self._range_expr_handlers
        ])

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        ranges = [
            reh.validator.range_after_validation
            for reh in self._range_expr_handlers
        ]
        return _LineNumRangeTransformerAdv(self._name, self.structure, ranges)


class _LineNumRangeTransformerAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 name: str,
                 structure_renderer: Callable[[], StructureRenderer],
                 ranges: Sequence[Range],
                 ):
        self._name = name
        self._structure_renderer = structure_renderer
        self._ranges = ranges

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        ranges = self._ranges

        return (
            transformers.SingleLineRangeTransformer(
                self._name,
                self._structure_renderer,
                ranges[0],
                environment.mem_buff_size,
            )
            if len(ranges) == 1
            else
            transformers.MultipleLineRangesTransformer(
                self._name,
                self._structure_renderer,
                ranges,
                environment.mem_buff_size,
            )
        )


class _RangeValidator(DdvValidator):
    def __init__(self, range_expr_: str):
        self._range_expr = range_expr_
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


class _StructureRenderer(NodeRenderer[None]):
    def __init__(self,
                 name: str,
                 ranges: Sequence[ToStringObject],
                 ):
        self._name = name
        self._ranges = ranges

    def render(self) -> Node[None]:
        return self._render().render()

    def _render(self) -> StructureRenderer:
        ranges = [
            (
                repr(r)
                if r == '' or r.isspace()
                else
                r
            )
            for r in [str(r) for r in self._ranges]
        ]
        range_list = ' '.join(ranges)
        return renderers.NodeRendererFromParts(
            self._name,
            None,
            (details.String(range_list),),
            (),
        )
