from abc import ABC
from typing import TypeVar, Sequence, Generic, Callable

from exactly_lib.impls.types.matcher.impls import combinator_matchers
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class Negation(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self, operand: MatcherSdv[MODEL]):
        self._operand = operand

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._operand.references

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


class InfixOpImplBase(Generic[MODEL], MatcherSdv[MODEL], ABC):
    def __init__(self,
                 operands: Sequence[MatcherSdv[MODEL]],
                 model_freezer: Callable[[MODEL], MODEL],
                 ):
        self._operands = operands
        self._model_freezer = model_freezer
        self._references = references_from_objects_with_symbol_references(operands)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class Conjunction(InfixOpImplBase[MODEL]):
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return combinator_matchers.ConjunctionDdv(
            [operand.resolve(symbols)
             for operand in self._operands],
            self._model_freezer,
        )


class Disjunction(InfixOpImplBase[MODEL]):
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return combinator_matchers.DisjunctionDdv(
            [operand.resolve(symbols)
             for operand in self._operands],
            self._model_freezer,
        )
