from typing import TypeVar, Generic, Optional, Sequence, Callable

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.matcher.object import ObjectDdv, ObjectSdv
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv, MODEL, MatcherWTrace
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ComparisonMatcher(Generic[T], MatcherWTrace[T]):
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs: T,
                 model_renderer: Callable[[T], DetailsRenderer],
                 ):
        self._model_renderer = model_renderer
        self._rhs = rhs
        self._operator = operator

    @staticmethod
    def new_structure_tree(op: comparators.ComparisonOperator,
                           rhs: DetailsRenderer) -> StructureRenderer:
        return _StructureRenderer(
            op,
            rhs,
            None,
            None,
        )

    @property
    def name(self) -> str:
        return self._operator.name

    def structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            self._operator,
            self._model_renderer(self._rhs),
        )

    def matches_w_trace(self, model: T) -> MatchingResult:
        lhs = model
        comparison_fun = self._operator.operator_fun
        condition_is_satisfied = bool(comparison_fun(lhs, self._rhs))
        return MatchingResult(
            condition_is_satisfied,
            _StructureRenderer(
                self._operator,
                self._model_renderer(self._rhs),
                condition_is_satisfied,
                self._model_renderer(lhs),
            ),
        )


class _StructureRenderer(Generic[T], NodeRenderer[T]):
    def __init__(self,
                 op: comparators.ComparisonOperator,
                 rhs: DetailsRenderer,
                 data: T,
                 actual_lhs: Optional[DetailsRenderer],
                 ):
        self._op = op
        self._rhs = rhs
        self._data = data
        self._actual_lhs = actual_lhs

    def render(self) -> Node[None]:
        ds = list(custom_details.rhs(self._rhs).render())
        if self._actual_lhs is not None:
            ds += custom_details.actual_lhs(self._actual_lhs).render()

        return Node(
            self._op.name,
            self._data,
            ds,
            ()
        )


class ComparisonMatcherDdv(Generic[T], MatcherDdv[T]):
    def __init__(self,
                 op: comparators.ComparisonOperator,
                 rhs: ObjectDdv[T],
                 model_renderer: Callable[[T], DetailsRenderer],
                 ):
        self._rhs = rhs
        self._operator = op
        self._model_renderer = model_renderer

    def structure(self) -> StructureRenderer:
        return ComparisonMatcher.new_structure_tree(
            self._operator,
            self._rhs.describer(),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._rhs.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            ComparisonMatcher(
                self._operator,
                self._rhs.value_of_any_dependency(tcds),
                self._model_renderer,
            )
        )


class ComparisonMatcherSdv(Generic[T], MatcherSdv[T]):
    def __init__(self,
                 op: comparators.ComparisonOperator,
                 rhs: ObjectSdv[T],
                 model_renderer: Callable[[T], DetailsRenderer],
                 ):
        self._rhs = rhs
        self._operator = op
        self._model_renderer = model_renderer

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._rhs.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[T]:
        return ComparisonMatcherDdv(
            self._operator,
            self._rhs.resolve(symbols),
            self._model_renderer,
        )
