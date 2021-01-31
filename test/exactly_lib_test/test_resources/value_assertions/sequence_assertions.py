from typing import TypeVar, Sequence

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion

T = TypeVar('T')


def matches_elements_except_last(elements: Assertion[Sequence[T]]) -> Assertion[Sequence[T]]:
    return asrt.on_transformed2(
        lambda l: l[:-1],
        elements,
        'all but last element'
    )


def is_non_empty_and_first_element(first_element: Assertion[T]) -> Assertion[Sequence[T]]:
    return asrt.and_([
        asrt.length(asrt.gt(0)),
        asrt.sequence_elem_at_index(
            0,
            first_element,
        )
    ])


def tail_matches(elements: Sequence[Assertion[T]]) -> Assertion[Sequence[T]]:
    return asrt.on_transformed2(
        lambda l: l[-(len(elements)):],
        asrt.matches_sequence(elements),
        'last {} elements'.format(len(elements))
    )
