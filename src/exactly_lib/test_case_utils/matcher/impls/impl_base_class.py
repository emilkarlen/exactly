from abc import ABC
from typing import Generic

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MODEL


class MatcherImplBase(Generic[MODEL],
                      MatcherWTraceAndNegation[MODEL],
                      WithCachedNameAndTreeStructureDescriptionBase,
                      ABC):
    def __init__(self):
        WithCachedNameAndTreeStructureDescriptionBase.__init__(self)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)

    @property
    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return combinator_matchers.Negation(self)
