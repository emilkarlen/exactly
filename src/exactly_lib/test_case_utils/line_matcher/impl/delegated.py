from typing import Optional, List

from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine, LineMatcherDdv
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation, MatcherDdv
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


class LineMatcherValueDelegatedToMatcher(LineMatcherDdv):
    def __init__(self, delegated: MatcherDdv[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    def structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._delegated.validator

    def value_of_any_dependency(self, tcds: Tcds) -> LineMatcher:
        return LineMatcherDelegatedToMatcher(self._delegated.value_of_any_dependency(tcds))


class LineMatcherSdvDelegatedToMatcher(LineMatcherSdv):
    def __init__(self, delegated: MatcherSdv[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._delegated.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(self._value_validator)

    def resolve(self, symbols: SymbolTable) -> LineMatcherDdv:
        return LineMatcherValueDelegatedToMatcher(self._delegated.resolve(symbols))

    def _value_validator(self, symbols: SymbolTable) -> PreOrPostSdsValueValidator:
        return self._delegated.resolve(symbols).validator
