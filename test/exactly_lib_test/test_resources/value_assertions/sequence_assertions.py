from typing import TypeVar, Sequence

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

T = TypeVar('T')


def matches_elements_except_last(elements: ValueAssertion[Sequence[T]]) -> ValueAssertion[Sequence[T]]:
    return asrt.on_transformed2(
        lambda l: l[:-1],
        elements,
        'all but last element'
    )


def tail_matches(elements: Sequence[ValueAssertion[T]]) -> ValueAssertion[Sequence[T]]:
    return asrt.on_transformed2(
        lambda l: l[:(len(elements))],
        asrt.matches_sequence(elements),
        'last {} elements'.format(len(elements))
    )
