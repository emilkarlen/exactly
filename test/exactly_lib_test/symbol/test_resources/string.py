from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as \
    asrt_restr
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolTableValue, SdvSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_STRING_REFERENCE_RESTRICTION = asrt_restr.equals_data_type_reference_restrictions(
    string_made_up_by_just_strings())

IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION = asrt_restr.equals_data_type_reference_restrictions(
    string_made_up_by_just_strings())


def is_string_made_up_of_just_strings_reference_to(name_of_symbol: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_symbol),
                                            IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)


def is_string_made_up_of_just_strings_reference_to__ref(name_of_symbol: str,
                                                        ) -> ValueAssertion[SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_symbol),
                                                 IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)


class StringSymbolTableValue(SymbolTableValue[StringSdv]):
    @staticmethod
    def of_sdv(sdv: StringSdv) -> 'StringSymbolTableValue':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return StringSymbolTableValue(sdv)

    @staticmethod
    def of_constant(primitive: str) -> 'StringSymbolTableValue':
        return StringSymbolTableValue(string_sdvs.str_constant(primitive))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(
            symbol_name,
            asrt_restr.is_string_value_restriction
        )

    @staticmethod
    def reference_assertion__any_data_type(symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(
            symbol_name,
            asrt_restr.is_any_data_type_reference_restrictions()
        )

    @staticmethod
    def usage_assertion__any_data_type(symbol_name: str) -> ValueAssertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference_2(
            symbol_name,
            asrt_restr.is_any_data_type_reference_restrictions()
        )

    @staticmethod
    def reference_assertion__string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_string_made_up_of_just_strings_reference_to__ref(symbol_name)

    @staticmethod
    def usage_assertion__string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolUsage]:
        return is_string_made_up_of_just_strings_reference_to(symbol_name)


class StringSymbolContext(SdvSymbolContext[StringSdv]):
    def __init__(self,
                 name: str,
                 value: StringSymbolTableValue,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str, sdv: StringSdv) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolTableValue.of_sdv(sdv)
        )

    @staticmethod
    def of_constant(name: str, primitive: str) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolTableValue.of_constant(primitive)
        )

    @property
    def reference_assertion__any_data_type(self) -> ValueAssertion[SymbolReference]:
        return StringSymbolTableValue.reference_assertion__any_data_type(self.name)

    @property
    def usage_assertion__any_data_type(self) -> ValueAssertion[SymbolUsage]:
        return StringSymbolTableValue.usage_assertion__any_data_type(self.name)

    @property
    def reference_assertion__string_made_up_of_just_strings(self) -> ValueAssertion[SymbolReference]:
        return StringSymbolTableValue.reference_assertion__string_made_up_of_just_strings(self.name)

    @property
    def usage_assertion__string_made_up_of_just_strings(self) -> ValueAssertion[SymbolUsage]:
        return StringSymbolTableValue.usage_assertion__string_made_up_of_just_strings(self.name)


class StringConstantSymbolContext(StringSymbolContext):
    def __init__(self,
                 name: str,
                 constant: str,
                 ):
        super().__init__(name, StringSymbolTableValue.of_constant(constant))
        self._constant = constant

    @property
    def str_value(self) -> str:
        return self._constant
