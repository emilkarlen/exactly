from typing import Sequence

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult, MODEL, \
    MatcherWTraceAndNegation
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck
from exactly_lib.util.description_tree import renderers


class StringMatcherNegation(MatcherWTraceAndNegation[FileToCheck],
                            WithCachedTreeStructureDescriptionBase,
                            ):
    NAME = expression.NOT_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(negated: WithTreeStructureDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            StringMatcherNegation.NAME,
            None,
            (),
            (negated.structure(),),
        )

    def __init__(self, operand: StringMatcher):
        WithCachedTreeStructureDescriptionBase.__init__(self)
        self._operand = operand

    @property
    def name(self) -> str:
        return self.NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._operand)

    def negation(self) -> StringMatcher:
        return self._operand

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        result_to_negate = self._operand.matches_w_trace(model)
        return (
            TraceBuilder(self.name)
                .append_child(result_to_negate.trace)
                .build_result(not result_to_negate.value)
        )

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._operand,
