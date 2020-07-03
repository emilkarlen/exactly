from abc import ABC
from typing import Generic, Sequence, Callable

from exactly_lib.definitions import logic
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatcherDdv, MODEL, MatcherAdv
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers


class _CombinatorBase(Generic[MODEL],
                      WithCachedNameAndTreeStructureDescriptionBase,
                      MatcherWTrace[MODEL],
                      ABC):
    def __init__(self):
        WithCachedNameAndTreeStructureDescriptionBase.__init__(self)


class Negation(_CombinatorBase[MODEL]):
    NAME = logic.NOT_OPERATOR_NAME

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

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._negated)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        result_to_negate = self._negated.matches_w_trace(model)
        return (
            TraceBuilder(self.name)
                .append_child(result_to_negate.trace)
                .build_result(not result_to_negate.value)
        )

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._negated,


class _NegationAdv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self, operand: MatcherAdv[MODEL]):
        self._operand = operand

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return Negation(self._operand.primitive(environment))


class NegationDdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self, operand: MatcherDdv[MODEL]):
        self._operand = operand

    def structure(self) -> StructureRenderer:
        return Negation.new_structure_tree(self._operand)

    @property
    def validator(self) -> DdvValidator:
        return self._operand.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _NegationAdv(self._operand.value_of_any_dependency(tcds))


class _SequenceOfOperandsAdv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self,
                 make_matcher: Callable[[Sequence[MatcherWTrace[MODEL]]], MatcherWTrace[MODEL]],
                 operands: Sequence[MatcherAdv[MODEL]],
                 ):
        self._make_matcher = make_matcher
        self._operands = operands

    @staticmethod
    def of(
            make_matcher: Callable[[Sequence[MatcherWTrace[MODEL]]], MatcherWTrace[MODEL]],
            operands: Sequence[MatcherDdv[MODEL]],
            tcds: Tcds,
    ) -> MatcherAdv[MODEL]:
        return _SequenceOfOperandsAdv(
            make_matcher,
            [
                operand.value_of_any_dependency(tcds)
                for operand in operands
            ]
        )

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return self._make_matcher([
            operand.primitive(environment)
            for operand in self._operands
        ])


class Conjunction(_CombinatorBase[MODEL]):
    NAME = logic.AND_OPERATOR_NAME

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

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._parts)

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


class ConjunctionDdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self, operands: Sequence[MatcherDdv[MODEL]]):
        self._operands = operands
        self._validator = ddv_validators.all_of(
            [matcher.validator
             for matcher in operands]
        )

    def structure(self) -> StructureRenderer:
        return Conjunction.new_structure_tree(self._operands)

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _SequenceOfOperandsAdv.of(Conjunction,
                                         self._operands,
                                         tcds)


def conjunction_adv(operands: Sequence[MatcherAdv[MODEL]]) -> MatcherAdv[MODEL]:
    return _SequenceOfOperandsAdv(Conjunction, operands)


class Disjunction(_CombinatorBase[MODEL]):
    NAME = logic.OR_OPERATOR_NAME

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

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._parts)

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


class DisjunctionDdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self, operands: Sequence[MatcherDdv[MODEL]]):
        self._operands = operands
        self._validator = ddv_validators.all_of(
            [matcher.validator
             for matcher in operands]
        )

    def structure(self) -> StructureRenderer:
        return Disjunction.new_structure_tree(self._operands)

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _SequenceOfOperandsAdv.of(Disjunction,
                                         self._operands,
                                         tcds)
