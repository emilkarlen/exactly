from abc import ABC
from typing import Optional, Generic

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.description import trace_renderers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation, MODEL


class MatcherImplBase(Generic[MODEL],
                      MatcherWTraceAndNegation[MODEL],
                      WithCachedNameAndTreeStructureDescriptionBase,
                      ABC):
    def __init__(self):
        WithCachedNameAndTreeStructureDescriptionBase.__init__(self)

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('deprecated')

    def matches(self, model: MODEL) -> bool:
        raise NotImplementedError('abstract method')

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        mb_emr = self.matches_emr(model)

        tb = self._new_tb()

        if mb_emr is None:
            return tb.build_result(True)
        else:
            tb.details.append(
                trace_renderers.DetailsRendererOfErrorMessageResolver(mb_emr))
            return tb.build_result(False)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)

    @property
    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return combinator_matchers.Negation(self)
