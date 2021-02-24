from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Sequence, Callable

from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.interval.with_interval import WithIntInterval
from exactly_lib.impls.types.matcher.object import ObjectDdv, ObjectSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class Config(Generic[MODEL]):
    def __init__(self,
                 rhs_syntax_element: str,
                 operator: comparators.ComparisonOperator,
                 model_renderer: Callable[[MODEL], DetailsRenderer],
                 ):
        self.rhs_syntax_element = rhs_syntax_element
        self.operator = operator
        self.model_renderer = model_renderer


class ComparisonMatcher(Generic[MODEL], MatcherWTrace[MODEL]):
    def __init__(self,
                 config: Config[MODEL],
                 rhs: MODEL,
                 ):
        self._operator = config.operator
        self._rhs_syntax_element = config.rhs_syntax_element
        self._model_renderer = config.model_renderer
        self._rhs = rhs

    @staticmethod
    def new_structure_tree(rhs_syntax_element: str,
                           op: comparators.ComparisonOperator,
                           rhs: DetailsRenderer) -> StructureRenderer:
        return _StructureRenderer(
            rhs_syntax_element,
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
            self._rhs_syntax_element,
            self._operator,
            self._model_renderer(self._rhs),
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        lhs = model
        comparison_fun = self._operator.operator_fun
        condition_is_satisfied = bool(comparison_fun(lhs, self._rhs))
        return MatchingResult(
            condition_is_satisfied,
            _StructureRenderer(
                self._rhs_syntax_element,
                self._operator,
                self._model_renderer(self._rhs),
                condition_is_satisfied,
                self._model_renderer(lhs),
            ),
        )


class IntComparisonMatcher(ComparisonMatcher[int], WithIntInterval):
    @property
    def interval(self) -> IntIntervalWInversion:
        return self._operator.int_interval(self._rhs)


class PrimitiveConstructionConfig(Generic[MODEL], ABC):
    def __init__(self, config: Config[MODEL]):
        self.config = config

    @abstractmethod
    def mk_primitive(self, rhs: MODEL) -> ComparisonMatcher[MODEL]:
        pass


class AnyModelConstructionConfig(Generic[MODEL], PrimitiveConstructionConfig[MODEL]):
    def mk_primitive(self, rhs: MODEL) -> ComparisonMatcher[MODEL]:
        return ComparisonMatcher(self.config, rhs)


class IntModelConstructionConfig(PrimitiveConstructionConfig[int]):
    def mk_primitive(self, rhs: int) -> IntComparisonMatcher:
        return IntComparisonMatcher(self.config, rhs)


class _StructureRenderer(Generic[T], NodeRenderer[T]):
    def __init__(self,
                 rhs_syntax_element: str,
                 op: comparators.ComparisonOperator,
                 rhs: DetailsRenderer,
                 data: T,
                 actual_lhs: Optional[DetailsRenderer],
                 ):
        self._rhs_syntax_element = rhs_syntax_element
        self._op = op
        self._rhs = rhs
        self._data = data
        self._actual_lhs = actual_lhs

    def render(self) -> Node[T]:
        ds = list(custom_details.expected_rhs(self._rhs).render())
        if self._actual_lhs is not None:
            ds += custom_details.actual_lhs(self._actual_lhs).render()

        return Node(
            ' '.join((self._op.name, self._rhs_syntax_element)),
            self._data,
            ds,
            ()
        )


class ComparisonMatcherDdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 construction_config: PrimitiveConstructionConfig[MODEL],
                 rhs: ObjectDdv[MODEL],
                 ):
        self._config = construction_config
        self._rhs = rhs

    def structure(self) -> StructureRenderer:
        return ComparisonMatcher.new_structure_tree(
            self._config.config.rhs_syntax_element,
            self._config.config.operator,
            self._rhs.describer(),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._rhs.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            self._config.mk_primitive(self._rhs.value_of_any_dependency(tcds))
        )


class ComparisonMatcherSdv(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self,
                 construction_config: PrimitiveConstructionConfig[MODEL],
                 rhs: ObjectSdv[MODEL],
                 ):
        self._config = construction_config
        self._rhs = rhs

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._rhs.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return ComparisonMatcherDdv(
            self._config,
            self._rhs.resolve(symbols),
        )
