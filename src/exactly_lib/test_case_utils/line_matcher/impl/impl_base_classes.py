from abc import ABC
from typing import Optional

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.type_system.description import trace_renderers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult


class LineMatcherImplBase(WithCachedTreeStructureDescriptionBase,
                          LineMatcher,
                          ABC):
    """
    Matches text lines.

    A line is a tuple (line number, line contents).

    Line numbers start at 1.
    """

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        mb_fail = self.matches_emr(line)

        tb = self._new_tb()

        if mb_fail is None:
            return tb.build_result(True)
        else:
            tb.details.append(
                trace_renderers.DetailsRendererOfErrorMessageResolver(mb_fail))
            return tb.build_result(False)

    def matches_emr(self, line: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        if self.matches(line):
            return None
        else:
            return err_msg_resolvers.constant('Lines does not match')

    def matches(self, line: LineMatcherLine) -> bool:
        """
        :return: If the line matches the condition represented by the matcher
        """
        raise NotImplementedError('abstract method of ' + str(type(self)))
