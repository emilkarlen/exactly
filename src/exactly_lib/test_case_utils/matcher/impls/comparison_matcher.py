import operator
from typing import TypeVar, Generic, Optional, Sequence, Callable

from exactly_lib.definitions import logic
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.matcher.object import ObjectDdv, ObjectSdv
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv, MODEL
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation
from exactly_lib.util import logic_types
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ComparisonMatcher(Generic[T], MatcherWTraceAndNegation[T]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 operator: comparators.ComparisonOperator,
                 rhs: T,
                 model_renderer: Callable[[T], DetailsRenderer],
                 ):
        self._model_renderer = model_renderer
        self._expectation_type = expectation_type
        self._rhs = rhs
        self._operator = operator

    @staticmethod
    def new_structure_tree(expectation_type: ExpectationType,
                           op: comparators.ComparisonOperator,
                           rhs: DetailsRenderer) -> StructureRenderer:
        return _StructureRenderer(
            expectation_type,
            op,
            rhs,
            None,
            lambda x: x,
            None,
        )

    @property
    def name(self) -> str:
        return self._operator.name

    def structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            self._expectation_type,
            self._operator,
            self._model_renderer(self._rhs),
        )

    @property
    def negation(self) -> MatcherWTraceAndNegation[T]:
        return ComparisonMatcher(
            logic_types.negation(self._expectation_type),
            self._operator,
            self._rhs,
            self._model_renderer,
        )

    def matches_w_trace(self, model: T) -> MatchingResult:
        lhs = model
        comparison_fun = self._operator.operator_fun
        condition_is_satisfied = bool(comparison_fun(lhs,
                                                     self._rhs))
        result = (
            condition_is_satisfied
            if self._expectation_type is ExpectationType.POSITIVE
            else
            not condition_is_satisfied
        )

        return MatchingResult(
            result,
            _StructureRenderer(
                self._expectation_type,
                self._operator,
                self._model_renderer(self._rhs),
                condition_is_satisfied,
                operator.not_,
                self._model_renderer(lhs),
            ),
        )


class _TraceRenderer(Generic[T], NodeRenderer[bool]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 operator: comparators.ComparisonOperator,
                 lhs_from_model: T,
                 rhs: T,
                 result__wo_expectation_type: bool,
                 model_renderer: Callable[[T], str],
                 ):
        self._expectation_type = expectation_type
        self._rhs = rhs
        self._lhs_from_model = lhs_from_model
        self._operator = operator
        self._result__wo_expectation_type = result__wo_expectation_type
        self._model_renderer = model_renderer

    def render(self) -> Node[bool]:
        header = ' '.join((self._operator.name,
                           self._model_renderer(self._rhs)))
        comparison_node = Node(
            header,
            self._result__wo_expectation_type,
            custom_details.actual(details.String(self._model_renderer(self._lhs_from_model))).render(),
            ()
        )

        return (
            comparison_node
            if self._expectation_type is ExpectationType.POSITIVE
            else
            Node(
                logic.NOT_OPERATOR_NAME,
                not self._result__wo_expectation_type,
                (),
                [comparison_node]
            )
        )


class _StructureRenderer(Generic[T], NodeRenderer[T]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 op: comparators.ComparisonOperator,
                 rhs: DetailsRenderer,
                 data: T,
                 negate_data: Callable[[T], T],
                 actual_lhs: Optional[DetailsRenderer],
                 ):
        self._expectation_type = expectation_type
        self._op = op
        self._rhs = rhs
        self._data = data
        self._negate_data = negate_data
        self._actual_lhs = actual_lhs

    def render(self) -> Node[None]:
        ds = list(custom_details.rhs(self._rhs).render())
        if self._actual_lhs is not None:
            ds += custom_details.actual_lhs(self._actual_lhs).render()

        comparison_node = Node(
            self._op.name,
            self._data,
            ds,
            ()
        )

        return (
            comparison_node
            if self._expectation_type is ExpectationType.POSITIVE
            else
            Node(
                logic.NOT_OPERATOR_NAME,
                self._negate_data(self._data),
                (),
                (comparison_node,)
            )
        )


class ComparisonMatcherDdv(Generic[T], MatcherDdv[T]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 op: comparators.ComparisonOperator,
                 rhs: ObjectDdv[T],
                 model_renderer: Callable[[T], DetailsRenderer],
                 ):
        self._expectation_type = expectation_type
        self._rhs = rhs
        self._operator = op
        self._model_renderer = model_renderer

    def structure(self) -> StructureRenderer:
        return ComparisonMatcher.new_structure_tree(
            self._expectation_type,
            self._operator,
            self._rhs.describer(),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._rhs.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            ComparisonMatcher(
                self._expectation_type,
                self._operator,
                self._rhs.value_of_any_dependency(tcds),
                self._model_renderer,
            )
        )


class ComparisonMatcherSdv(Generic[T], MatcherSdv[T]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 op: comparators.ComparisonOperator,
                 rhs: ObjectSdv[T],
                 model_renderer: Callable[[T], DetailsRenderer],
                 ):
        self._expectation_type = expectation_type
        self._rhs = rhs
        self._operator = op
        self._model_renderer = model_renderer

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._rhs.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[T]:
        return ComparisonMatcherDdv(
            self._expectation_type,
            self._operator,
            self._rhs.resolve(symbols),
            self._model_renderer,
        )
