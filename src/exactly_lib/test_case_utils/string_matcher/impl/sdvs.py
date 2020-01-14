from typing import Sequence, Callable

from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs, sdv_components
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.test_case_utils.string_matcher.impl import on_transformed
from exactly_lib.type_system.logic.string_matcher import StringMatcherDdv, GenericStringMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def new_maybe_negated(matcher: GenericStringMatcherSdv,
                      expectation_type: ExpectationType) -> StringMatcherSdv:
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return StringMatcherSdv(matcher)


def new_with_transformation(transformer: StringTransformerSdv,
                            original: GenericStringMatcherSdv) -> StringMatcherSdv:
    return StringMatcherSdv(on_transformed.StringMatcherWithTransformationSdv(transformer, original))


def new_with_transformation__generic(transformer: StringTransformerSdv,
                                     original: GenericStringMatcherSdv) -> GenericStringMatcherSdv:
    return on_transformed.StringMatcherWithTransformationSdv(transformer, original)


def new_reference(name_of_referenced_sdv: str,
                  expectation_type: ExpectationType) -> StringMatcherSdv:
    matcher = MatcherReferenceSdv(name_of_referenced_sdv, ValueType.STRING_MATCHER)
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return StringMatcherSdv(matcher)


def new_reference__generic(name_of_referenced_sdv: str,
                           expectation_type: ExpectationType) -> GenericStringMatcherSdv:
    matcher = MatcherReferenceSdv(name_of_referenced_sdv, ValueType.STRING_MATCHER)
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return matcher


def string_matcher_sdv_from_parts_2(references: Sequence[SymbolReference],
                                    get_ddv: Callable[[SymbolTable], StringMatcherDdv]) -> StringMatcherSdv:
    return StringMatcherSdv(
        sdv_components.MatcherSdvFromParts(references, get_ddv)
    )
