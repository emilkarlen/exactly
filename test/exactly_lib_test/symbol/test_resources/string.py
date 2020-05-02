from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference, ReferenceRestrictions
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_utils.parse.parse_path import path_or_string_reference_restrictions, \
    PATH_COMPONENT_STRING_REFERENCES_RESTRICTION
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as \
    asrt_rest
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference, \
    symbol_usage_equals_symbol_reference
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbols_setup import DataTypeSymbolContext, \
    DataSymbolTypeContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_STRING_REFERENCE_RESTRICTION = asrt_rest.equals_data_type_reference_restrictions(
    string_made_up_by_just_strings())

IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION = asrt_rest.equals_data_type_reference_restrictions(
    string_made_up_by_just_strings())


def is_string_made_up_of_just_strings_reference_to(name_of_symbol: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_symbol),
                                            IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)


def is_string_made_up_of_just_strings_reference_to__ref(name_of_symbol: str,
                                                        ) -> ValueAssertion[SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_symbol),
                                                 IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)


class StringSymbolTypeContext(DataSymbolTypeContext[StringSdv]):
    @staticmethod
    def of_sdv(sdv: StringSdv) -> 'StringSymbolTypeContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return StringSymbolTypeContext(sdv)

    @staticmethod
    def of_constant(primitive: str) -> 'StringSymbolTypeContext':
        return StringSymbolTypeContext(string_sdvs.str_constant(primitive))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(
            symbol_name,
            asrt_rest.is_string_value_restriction
        )

    @staticmethod
    def reference_assertion__string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_string_made_up_of_just_strings_reference_to__ref(symbol_name)

    @staticmethod
    def usage_assertion__string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolUsage]:
        return is_string_made_up_of_just_strings_reference_to(symbol_name)

    @staticmethod
    def reference_restriction__path_or_string(accepted_relativities: PathRelativityVariants
                                              ) -> ReferenceRestrictions:
        return path_or_string_reference_restrictions(accepted_relativities)

    @staticmethod
    def reference_assertion__path_or_string(symbol_name: str,
                                            accepted_relativities: PathRelativityVariants,
                                            ) -> ValueAssertion[SymbolReference]:
        return equals_symbol_reference(
            SymbolReference(symbol_name,
                            StringSymbolTypeContext.reference_restriction__path_or_string(accepted_relativities))
        )

    @staticmethod
    def usage_assertion__path_or_string(symbol_name: str,
                                        accepted_relativities: PathRelativityVariants,
                                        ) -> ValueAssertion[SymbolUsage]:
        return symbol_usage_equals_symbol_reference(
            SymbolReference(symbol_name,
                            StringSymbolTypeContext.reference_restriction__path_or_string(accepted_relativities))
        )


class StringSymbolContext(DataTypeSymbolContext[StringSdv]):
    def __init__(self,
                 name: str,
                 type_context: StringSymbolTypeContext,
                 ):
        super().__init__(name, type_context)

    @staticmethod
    def of_sdv(name: str, sdv: StringSdv) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolTypeContext.of_sdv(sdv)
        )

    @staticmethod
    def of_constant(name: str, primitive: str) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolTypeContext.of_constant(primitive)
        )

    def reference__path_or_string(self, accepted_relativities: PathRelativityVariants) -> SymbolReference:
        return SymbolReference(self.name,
                               StringSymbolTypeContext.reference_restriction__path_or_string(accepted_relativities))

    @property
    def reference_assertion__string_made_up_of_just_strings(self) -> ValueAssertion[SymbolReference]:
        return StringSymbolTypeContext.reference_assertion__string_made_up_of_just_strings(self.name)

    @property
    def usage_assertion__string_made_up_of_just_strings(self) -> ValueAssertion[SymbolUsage]:
        return StringSymbolTypeContext.usage_assertion__string_made_up_of_just_strings(self.name)

    @property
    def reference_assertion__path_component(self) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference__ref(
            asrt.equals(self.name),
            asrt_rest.equals_data_type_reference_restrictions(PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
        )

    @property
    def usage_assertion__path_component(self) -> ValueAssertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference(
            asrt.equals(self.name),
            asrt_rest.equals_data_type_reference_restrictions(PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
        )

    def reference_assertion__path_or_string(self, accepted_relativities: PathRelativityVariants
                                            ) -> ValueAssertion[SymbolReference]:
        return StringSymbolTypeContext.reference_assertion__path_or_string(self.name, accepted_relativities)

    def usage_assertion__path_or_string(self, accepted_relativities: PathRelativityVariants
                                        ) -> ValueAssertion[SymbolUsage]:
        return StringSymbolTypeContext.usage_assertion__path_or_string(self.name, accepted_relativities)


class StringConstantSymbolContext(StringSymbolContext):
    def __init__(self,
                 name: str,
                 constant: str = 'string value',
                 ):
        super().__init__(name, StringSymbolTypeContext.of_constant(constant))
        self._constant = constant

    @property
    def str_value(self) -> str:
        return self._constant


class StringIntConstantSymbolContext(StringSymbolContext):
    def __init__(self,
                 name: str,
                 constant: int,
                 ):
        super().__init__(name, StringSymbolTypeContext.of_constant(str(constant)))
        self._int_constant = constant

    @property
    def int_value(self) -> int:
        return self._int_constant


def arbitrary_symbol_context(symbol_name: str) -> StringSymbolContext:
    return StringConstantSymbolContext(symbol_name, 'arbitrary value')


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringSymbolTypeContext.of_constant('arbitrary value')
