from exactly_lib.symbol.sdv_structure import SymbolUsage, ReferenceRestrictions
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_reference_2
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches_reference(expected: NameAndValue[Assertion[ReferenceRestrictions]]
                      ) -> Assertion[SymbolUsage]:
    return matches_reference_2(expected.name,
                               expected.value)
