from exactly_lib.util.str_.str_constructor import ToStringObject
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches(expected: Assertion[str]) -> Assertion[ToStringObject]:
    return asrt.sub_component('to_string',
                              str,
                              asrt.is_instance_with(str, expected),
                              )


def equals(expected: str) -> Assertion[ToStringObject]:
    return matches(asrt.equals(expected))
