from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_symbol_usages_is_singleton_list(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.matches_sequence([assertion])
