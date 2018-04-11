from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_reference_2
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_reference(expected: NameAndValue[asrt.ValueAssertion[ReferenceRestrictions]]
                      ) -> asrt.ValueAssertion[SymbolUsage]:
    return matches_reference_2(expected.name,
                               expected.value)
