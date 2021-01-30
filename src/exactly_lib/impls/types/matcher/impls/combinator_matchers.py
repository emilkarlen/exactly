from abc import ABC
from typing import Generic, Sequence, Callable

from exactly_lib.definitions import logic
from exactly_lib.impls.description_tree.tree_structured import WithCachedNameAndNodeStructureDescriptionBase
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.description.tree_structured import WithNodeDescription
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace, MODEL, T, \
    MatcherStdTypeVisitor
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers


class Negation(Generic[MODEL],
               WithCachedNameAndNodeStructureDescriptionBase,
               MatcherWTrace[MODEL],
               ):
    NAME = logic.NOT_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(negated: WithNodeDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Negation.NAME,
            None,
            (),
            (negated.structure(),),
        )

    def __init__(self, negated: MatcherWTrace[MODEL]):
        WithCachedNameAndNodeStructureDescriptionBase.__init__(self)
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

    def accept(self, visitor: MatcherStdTypeVisitor[MODEL, T]) -> T:
        return visitor.visit_negation(self._negated)

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

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return _NegationAdv(self._operand.value_of_any_dependency(tcds))


class _SequenceOfOperandsAdv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self,
                 make_matcher: Callable[
                     [Sequence[MatcherWTrace[MODEL]], Callable[[MODEL], MODEL]],
                     MatcherWTrace[MODEL]],
                 operands: Sequence[MatcherAdv[MODEL]],
                 model_freezer: Callable[[MODEL], MODEL],
                 ):
        self._make_matcher = make_matcher
        self._operands = operands
        self._model_freezer = model_freezer

    @staticmethod
    def of(
            make_matcher: Callable[[Sequence[MatcherWTrace[MODEL]], Callable[[MODEL], MODEL]], MatcherWTrace[MODEL]],
            operands: Sequence[MatcherDdv[MODEL]],
            model_freezer: Callable[[MODEL], MODEL],
            tcds: TestCaseDs,
    ) -> MatcherAdv[MODEL]:
        return _SequenceOfOperandsAdv(
            make_matcher,
            [
                operand.value_of_any_dependency(tcds)
                for operand in operands
            ],
            model_freezer,
        )

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return self._make_matcher([
            operand.primitive(environment)
            for operand in self._operands
        ],
            self._model_freezer,
        )


def no_op_freezer(model: MODEL) -> MODEL:
    return model


class _InfixOperatorBase(Generic[MODEL],
                         WithCachedNameAndNodeStructureDescriptionBase,
                         MatcherWTrace[MODEL],
                         ABC):

    def __init__(self,
                 operands: Sequence[MatcherWTrace[MODEL]],
                 model_freezer: Callable[[MODEL], MODEL] = no_op_freezer,
                 ):
        WithCachedNameAndNodeStructureDescriptionBase.__init__(self)
        self._operands = operands
        self._model_freezer = model_freezer


class Conjunction(Generic[MODEL], _InfixOperatorBase[MODEL]):
    NAME = logic.AND_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(operands: Sequence[WithNodeDescription]) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Conjunction.NAME,
            None,
            (),
            [operand.structure() for operand in operands],
        )

    @property
    def name(self) -> str:
        return self.NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._operands)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        model = self._model_freezer(model)
        tb = TraceBuilder(self.name)
        for operand in self._operands:
            result = operand.matches_w_trace(model)
            tb.append_child(result.trace)
            if not result.value:
                return tb.build_result(False)

        return tb.build_result(True)

    def accept(self, visitor: MatcherStdTypeVisitor[MODEL, T]) -> T:
        return visitor.visit_conjunction(self._operands)

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._operands


class ConjunctionDdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 operands: Sequence[MatcherDdv[MODEL]],
                 model_freezer: Callable[[MODEL], MODEL],
                 ):
        self._operands = operands
        self._model_freezer = model_freezer
        self._validator = ddv_validators.all_of(
            [matcher.validator
             for matcher in operands]
        )

    def structure(self) -> StructureRenderer:
        return Conjunction.new_structure_tree(self._operands)

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return _SequenceOfOperandsAdv.of(Conjunction,
                                         self._operands,
                                         self._model_freezer,
                                         tcds)


class Disjunction(Generic[MODEL], _InfixOperatorBase[MODEL]):
    NAME = logic.OR_OPERATOR_NAME

    @staticmethod
    def new_structure_tree(operands: Sequence[WithNodeDescription]) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Disjunction.NAME,
            None,
            (),
            [operand.structure() for operand in operands],
        )

    @property
    def name(self) -> str:
        return self.NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._operands)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        model = self._model_freezer(model)
        tb = TraceBuilder(self.name)
        for operand in self._operands:
            result = operand.matches_w_trace(model)
            tb.append_child(result.trace)
            if result.value:
                return tb.build_result(True)

        return tb.build_result(False)

    def accept(self, visitor: MatcherStdTypeVisitor[MODEL, T]) -> T:
        return visitor.visit_disjunction(self._operands)

    def _children(self) -> Sequence[MatcherWTrace[MODEL]]:
        return self._operands


class DisjunctionDdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 operands: Sequence[MatcherDdv[MODEL]],
                 model_freezer: Callable[[MODEL], MODEL],
                 ):
        self._operands = operands
        self._model_freezer = model_freezer
        self._validator = ddv_validators.all_of(
            [matcher.validator
             for matcher in operands]
        )

    def structure(self) -> StructureRenderer:
        return Disjunction.new_structure_tree(self._operands)

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return _SequenceOfOperandsAdv.of(Disjunction,
                                         self._operands,
                                         self._model_freezer,
                                         tcds)
