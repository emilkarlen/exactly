from typing import Sequence, Callable

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs, sdv_components
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.test_case_utils.string_matcher import string_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.type_system.logic.string_matcher import StringMatcherDdv, FileToCheck
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def new_with_transformation(transformer: StringTransformerSdv,
                            original: MatcherSdv[FileToCheck]) -> StringMatcherSdv:
    return StringMatcherSdv(_StringMatcherSvdWithTransformation(transformer, original))


def new_reference(name_of_referenced_sdv: str,
                  expectation_type: ExpectationType) -> StringMatcherSdv:
    matcher = MatcherReferenceSdv(name_of_referenced_sdv, ValueType.STRING_MATCHER)
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return StringMatcherSdv(matcher)


class _StringMatcherSvdWithTransformation(MatcherSdv[FileToCheck]):
    """
    A :class:`StringMatcherResolver` that transforms the model with a :class:`StringTransformerResolver`
    """

    def __init__(self,
                 transformer: StringTransformerSdv,
                 original: MatcherSdv[FileToCheck],
                 ):
        self._transformer = transformer
        self._original = original

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[FileToCheck]:
        return string_matchers.StringMatcherWithTransformationDdv(
            self._transformer.resolve(symbols),
            self._original.resolve(symbols),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return list(self._transformer.references) + list(self._original.references)

    def __str__(self):
        return str(type(self))


def string_matcher_sdv_from_parts_2(references: Sequence[SymbolReference],
                                    get_ddv: Callable[[SymbolTable], StringMatcherDdv]) -> StringMatcherSdv:
    return StringMatcherSdv(
        sdv_components.MatcherSdvFromParts(references, get_ddv)
    )
