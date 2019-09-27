from typing import Optional, List

from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.impls import matcher_combinators
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult


class FileMatcherDelegatedToMatcherWTrace(FileMatcher):
    def __init__(self, delegated: MatcherWTrace[FileMatcherModel]):
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    def negation(self) -> FileMatcher:
        return FileMatcherDelegatedToMatcherWTrace(self._delegated.negation)

    def matches(self, model: FileMatcherModel) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._delegated.matches_w_trace(model)


class FileMatcherNot(FileMatcherDelegatedToMatcherWTrace):
    """Matcher that negates a given matcher."""

    def __init__(self, matcher: FileMatcher):
        self._matcher = matcher
        super().__init__(matcher_combinators.Negation(matcher))

    @property
    def negation(self) -> FileMatcher:
        return self._matcher


class FileMatcherAnd(FileMatcherDelegatedToMatcherWTrace):
    """Matcher that and:s a list of matchers."""

    def __init__(self, matchers: List[FileMatcher]):
        self._matchers = matchers
        super().__init__(matcher_combinators.Conjunction(matchers))

    @property
    def matchers(self) -> List[FileMatcher]:
        return self._matchers


class FileMatcherOr(FileMatcherDelegatedToMatcherWTrace):
    """Matcher that or:s a list of matchers."""

    def __init__(self, matchers: List[FileMatcher]):
        self._matchers = matchers
        super().__init__(matcher_combinators.Disjunction(matchers))

    @property
    def matchers(self) -> List[FileMatcher]:
        return self._matchers
