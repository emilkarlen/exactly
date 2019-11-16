from typing import Optional, List

from exactly_lib.symbol.logic.resolver import MatcherResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
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


class StringMatcherResolverDelegatedToMatcher(StringMatcherResolver):
    def __init__(self, delegated: MatcherResolver[FileToCheck]):
        super().__init__()
        self._delegated = delegated

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._delegated.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(self._value_validator)

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return StringMatcherDdvDelegatedToMatcher(self._delegated.resolve(symbols))

    def _value_validator(self, symbols: SymbolTable) -> PreOrPostSdsValueValidator:
        return self._delegated.resolve(symbols).validator
