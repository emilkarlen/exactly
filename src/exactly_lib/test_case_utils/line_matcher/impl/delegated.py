from typing import Optional, Set, List

from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.logic.resolver import MatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine, LineMatcherValue
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation, MatcherValue
from exactly_lib.util.symbol_table import SymbolTable


class LineMatcherDelegatedToMatcher(LineMatcher):
    def __init__(self, delegated: MatcherWTraceAndNegation[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    def structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    @property
    def negation(self) -> LineMatcher:
        return LineMatcherDelegatedToMatcher(
            combinator_matchers.Negation(self)
        )

    def matches(self, model: LineMatcherLine) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        return self._delegated.matches_w_trace(model)


class LineMatcherValueDelegatedToMatcher(LineMatcherValue):
    def __init__(self, delegated: MatcherValue[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        """TODO Remove this functionality"""
        return set()

    def structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._delegated.validator

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LineMatcher:
        return LineMatcherDelegatedToMatcher(self._delegated.value_of_any_dependency(home_and_sds))


class LineMatcherResolverDelegatedToMatcher(LineMatcherResolver):
    def __init__(self, delegated: MatcherResolver[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._delegated.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(self._value_validator)

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return LineMatcherValueDelegatedToMatcher(self._delegated.resolve(symbols))

    def _value_validator(self, symbols: SymbolTable) -> PreOrPostSdsValueValidator:
        return self._delegated.resolve(symbols).validator
