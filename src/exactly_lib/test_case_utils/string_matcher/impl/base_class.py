from abc import ABC

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv, MatcherAdv
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck


class StringMatcherImplBase(WithCachedNameAndTreeStructureDescriptionBase,
                            MatcherWTraceAndNegation[FileToCheck],
                            ABC):

    @property
    def negation(self) -> StringMatcher:
        return combinator_matchers.Negation(self)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


class StringMatcherDdvImplBase(MatcherDdv[FileToCheck], ABC):
    pass


class StringMatcherAdvImplBase(MatcherAdv[FileToCheck], ABC):
    pass
