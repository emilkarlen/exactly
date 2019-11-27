from typing import Optional, List

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import sdv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace, MatcherDdv
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck, StringMatcherDdv
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherDelegatedToMatcher(StringMatcher):
    def __init__(self, delegated: MatcherWTrace[FileToCheck]):
        super().__init__()
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    def _structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    def matches(self, model: FileToCheck) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        return self._delegated.matches_w_trace(model)


class StringMatcherDdvDelegatedToMatcher(StringMatcherDdv):
    def __init__(self,
                 delegated: MatcherDdv[FileToCheck],
                 ):
        super().__init__()
        self._delegated = delegated

    def structure(self) -> StructureRenderer:
        return self._delegated.structure()

    def value_of_any_dependency(self, tcds: Tcds) -> StringMatcher:
        return StringMatcherDelegatedToMatcher(self._delegated.value_of_any_dependency(tcds))


class StringMatcherSdvDelegatedToMatcher(StringMatcherSdv):
    def __init__(self, delegated: MatcherSdv[FileToCheck]):
        super().__init__()
        self._delegated = delegated

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._delegated.references)

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.SdvValidatorFromDdvValidator(self._value_validator)

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return StringMatcherDdvDelegatedToMatcher(self._delegated.resolve(symbols))

    def _value_validator(self, symbols: SymbolTable) -> DdvValidator:
        return self._delegated.resolve(symbols).validator
