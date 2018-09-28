from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def assert_symbol_usages_is_singleton_list(assertion: ValueAssertion) -> ValueAssertion:
    return asrt.matches_sequence([assertion])
