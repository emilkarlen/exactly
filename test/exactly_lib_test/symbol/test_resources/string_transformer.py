from typing import Sequence

from exactly_lib.symbol.resolver_structure import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerValue
from exactly_lib.type_system.logic.string_transformer_values import StringTransformerConstantValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class StringTransformerResolverConstantTestImpl(StringTransformerResolver):
    def __init__(self,
                 resolved_value: StringTransformer,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> StringTransformer:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, named_elements: SymbolTable) -> StringTransformerValue:
        return StringTransformerConstantValue(self._resolved_value)


IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.STRING_TRANSFORMER)


def is_reference_to_string_transformer(name_of_transformer: str) -> asrt.ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_transformer),
                                            IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION)