from typing import TypeVar, Generic, Sequence

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_value_validation
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


def sdv_from_primitive_value(
        primitive_value: MatcherWTraceAndNegation[MODEL] = MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: PreOrPostSdsValueValidator = pre_or_post_value_validation.constant_success_validator(),
) -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(
        MatcherDdvOfConstantMatcherTestImpl(primitive_value,
                                            validator),
        references,
    )


def sdv_of_unconditionally_matching_matcher() -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(ddv_of_unconditionally_matching_matcher())


def ddv_of_unconditionally_matching_matcher() -> MatcherDdv[MODEL]:
    return MatcherDdvOfConstantMatcherTestImpl(
        MatcherWithConstantResult(True)
    )


class MatcherDdvOfConstantMatcherTestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 primitive_value: MatcherWTraceAndNegation[MODEL],
                 validator: PreOrPostSdsValueValidator =
                 pre_or_post_value_validation.constant_success_validator(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherWTraceAndNegation[MODEL]:
        return self._primitive_value


class MatcherSdvOfConstantDdvTestImpl(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self,
                 resolved_value: MatcherDdv[MODEL],
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> MatcherDdv[MODEL]:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return self._resolved_value
