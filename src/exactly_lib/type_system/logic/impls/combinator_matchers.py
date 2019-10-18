from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence, Optional

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult, MatcherWTraceAndNegation
from exactly_lib.util.description_tree import renderers

MODEL = TypeVar('MODEL')


class _CombinatorBase(Generic[MODEL],
                      WithCachedNameAndTreeStructureDescriptionBase,
                      MatcherWTraceAndNegation[MODEL],
                      ABC):
    def __init__(self):
        WithCachedNameAndTreeStructureDescriptionBase.__init__(self)

    @abstractmethod
    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        pass

    def _structure(self) -> StructureRenderer:
        children = [
            self._node_renderer_of(part)
            for part in self._children()
        ]
        return (
            self._new_structure_builder()
                .append_children(children)
                .build()
        )


class Negation(_CombinatorBase[MODEL]):
    NAME = expression.NOT_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(negated: WithTreeStructureDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Negation.NAME,
            None,
            (),
            (negated.structure(),),
        )

    def __init__(self, negated: MatcherWTrace[MODEL]):
        _CombinatorBase.__init__(self)
        self._negated = negated

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return expression.NOT_OPERATOR_NAME + ' ' + self._negated.option_description

    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return self._negated

    def matches(self, model: MODEL) -> bool:
        return not self._negated.matches(model)

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        mb_failure = self._negated.matches_emr(model)
        return (
            None
            if mb_failure
            else
            err_msg_resolvers.constant(' '.join([self.name, self._negated.name]))
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        result_to_negate = self._negated.matches_w_trace(model)
        return (
            TraceBuilder(self.name)
                .append_child(result_to_negate.trace)
                .build_result(not result_to_negate.value)
        )

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._negated,


class Conjunction(_CombinatorBase[MODEL]):
    NAME = expression.AND_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(operands: Sequence[WithTreeStructureDescription]) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Conjunction.NAME,
            None,
            (),
            [operand.structure() for operand in operands],
        )

    def __init__(self, parts: Sequence[MatcherWTrace[MODEL]]):
        _CombinatorBase.__init__(self)
        self._parts = parts

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return expression.AND_OPERATOR_NAME

    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return Negation(self)

    def matches(self, model: MODEL) -> bool:
        for part in self._parts:
            if not part.matches(model):
                return False

        return True

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        for part in self._parts:
            result = part.matches_emr(model)
            if result is not None:
                return result

        return None

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        tb = TraceBuilder(self.name)
        for part in self._parts:
            result = part.matches_w_trace(model)
            tb.append_child(result.trace)
            if not result.value:
                return tb.build_result(False)

        return tb.build_result(True)

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._parts


class Disjunction(_CombinatorBase[MODEL]):
    NAME = expression.OR_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(operands: Sequence[WithTreeStructureDescription]) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Disjunction.NAME,
            None,
            (),
            [operand.structure() for operand in operands],
        )

    def __init__(self, parts: Sequence[MatcherWTrace[MODEL]]):
        _CombinatorBase.__init__(self)
        self._parts = parts

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return expression.OR_OPERATOR_NAME

    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return Negation(self)

    def matches(self, model: MODEL) -> bool:
        for part in self._parts:
            if part.matches(model):
                return True

        return False

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        for part in self._parts:
            result = part.matches_emr(model)
            if result is None:
                return None

        return err_msg_resolvers.constant(self.name + ' F')

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        tb = TraceBuilder(self.name)
        for part in self._parts:
            result = part.matches_w_trace(model)
            tb.append_child(result.trace)
            if result.value:
                return tb.build_result(True)

        return tb.build_result(False)

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._parts
