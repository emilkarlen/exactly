from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import resolver_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

IS_PROGRAM_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.PROGRAM)


def is_program_reference_to(symbol_name: str) -> asrt.ValueAssertion:
    return asrt_sym.matches_reference(asrt.equals(symbol_name),
                                      IS_PROGRAM_REFERENCE_RESTRICTION)
