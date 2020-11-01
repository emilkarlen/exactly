import unittest
from typing import Sequence, Generic, Callable

from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherStdTypeVisitor, T, MatcherWTrace, MODEL
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class MatcherStdTypeVisitorTestAcceptImpl(Generic[MODEL, T], MatcherStdTypeVisitor[MODEL, T]):
    def __init__(self,
                 constant_action: Callable[[bool], T],
                 negation_action: Callable[[MatcherWTrace[MODEL]], T],
                 conjunction_action: Callable[[Sequence[MatcherWTrace[MODEL]]], T],
                 disjunction_action: Callable[[Sequence[MatcherWTrace[MODEL]]], T],
                 non_standard_action: Callable[[MatcherWTrace[MODEL]], T],
                 ):
        self._constant_action = constant_action
        self._negation_action = negation_action
        self._conjunction_action = conjunction_action
        self._disjunction_action = disjunction_action
        self._non_standard_action = non_standard_action

    @staticmethod
    def new_w_default_to_raise_exception(
            constant_action: Callable[[bool], T] =
            do_raise(ValueError('constant method must not be invoked')),
            negation_action: Callable[[MatcherWTrace[MODEL]], T] =
            do_raise(ValueError('negation method must not be invoked')),
            conjunction_action: Callable[[Sequence[MatcherWTrace[MODEL]]], T] =
            do_raise(ValueError('conjunction method must not be invoked')),
            disjunction_action: Callable[[Sequence[MatcherWTrace[MODEL]]], T] =
            do_raise(ValueError('disjunction method must not be invoked')),
            non_standard_action: Callable[[MatcherWTrace[MODEL]], T] =
            do_raise(ValueError('non_standard method must not be invoked')),
    ) -> MatcherStdTypeVisitor[MODEL, T]:
        return MatcherStdTypeVisitorTestAcceptImpl(
            constant_action,
            negation_action,
            conjunction_action,
            disjunction_action,
            non_standard_action,
        )

    def visit_constant(self, value: bool) -> T:
        return self._constant_action(value)

    def visit_negation(self, operand: MatcherWTrace[MODEL]) -> T:
        return self._negation_action(operand)

    def visit_conjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> T:
        return self._conjunction_action(operands)

    def visit_disjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> T:
        return self._disjunction_action(operands)

    def visit_non_standard(self, matcher: MatcherWTrace[MODEL]) -> T:
        return self._non_standard_action(matcher)


def assert_argument_satisfies__and_return(put: unittest.TestCase,
                                          argument_assertion: ValueAssertion,
                                          return_value) -> Callable:
    def ret_val(argument):
        argument_assertion.apply_with_message(put, argument, 'argument')
        return return_value

    return ret_val
