from abc import ABC
from typing import TypeVar, Sequence, Generic

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.util.logic_types import ExpectationType
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


def optionally_negated(matcher: MatcherSdv[MODEL],
                       expectation_type: ExpectationType) -> MatcherSdv[MODEL]:
    return (
        matcher
        if expectation_type is ExpectationType.POSITIVE
        else
        Negation(matcher)
    )


def new_maybe_negated(matcher: MatcherSdv[MODEL],
                      expectation_type: ExpectationType) -> MatcherSdv[MODEL]:
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = Negation(matcher)

    return matcher


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
