from typing import Any

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches(expected: ValueAssertion[str]) -> ValueAssertion[Any]:
    return asrt.sub_component('to_string',
                              str,
                              asrt.is_instance_with(str, expected),
                              )


def equals(expected: str) -> ValueAssertion[Any]:
    return matches(asrt.equals(expected))
