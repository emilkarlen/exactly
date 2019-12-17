from abc import ABC
from typing import TypeVar, Sequence, Generic

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class _ImplBase(Generic[MODEL], MatcherSdv[MODEL], ABC):
    def __init__(self, operands: Sequence[MatcherSdv[MODEL]]):
        self._operands = operands
        self._references = references_from_objects_with_symbol_references(operands)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class Negation(_ImplBase[MODEL]):
    def __init__(self, operand: MatcherSdv[MODEL]):
        super().__init__((operand,))
        self._operand = operand

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return combinator_matchers.NegationDdv(self._operand.resolve(symbols))


class Conjunction(_ImplBase[MODEL]):
    def __init__(self, operands: Sequence[MatcherSdv[MODEL]]):
        super().__init__(operands)

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return combinator_matchers.ConjunctionDdv(
            [operand.resolve(symbols)
             for operand in self._operands]
        )


class Disjunction(_ImplBase[MODEL]):
    def __init__(self, operands: Sequence[MatcherSdv[MODEL]]):
        super().__init__(operands)

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return combinator_matchers.DisjunctionDdv(
            [operand.resolve(symbols)
             for operand in self._operands]
        )
