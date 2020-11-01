from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference, ReferenceRestrictions, SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType, DataValueType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.type_val_deps.types.string import string_sdvs
from exactly_lib.type_val_deps.types.string.string_sdv import StringSdv
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building2 import StringMatcherArg
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion as asrt_rest
from exactly_lib_test.type_val_deps.data.test_resources.symbol_context import DataSymbolValueContext, \
    DataTypeSymbolContext
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    symbol_usage_equals_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.string.test_resources import sdv_assertions as asrt_value
from exactly_lib_test.type_val_deps.types.string.test_resources.string_sdvs import string_sdv_of_single_symbol_reference

IS_STRING_REFERENCE_RESTRICTION = asrt_rest.equals_data_type_reference_restrictions(
    string_made_up_by_just_strings())

IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION = asrt_rest.equals_data_type_reference_restrictions(
    string_made_up_by_just_strings())


def is_reference_to_string_made_up_of_just_strings__usage(name_of_symbol: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_symbol),
                                            IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)


def is_reference_to_string_made_up_of_just_strings(name_of_symbol: str,
                                                   ) -> ValueAssertion[SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_symbol),
                                                 IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)


class StringSymbolValueContext(DataSymbolValueContext[StringSdv]):
    def __init__(self,
                 sdv: StringSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
                 ):
        super().__init__(sdv, definition_source)
        self._default_restrictions = default_restrictions

    @staticmethod
    def of_sdv(sdv: StringSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
               ) -> 'StringSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return StringSymbolValueContext(sdv, definition_source, default_restrictions)

    @staticmethod
    def of_constant(primitive: str,
                    definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                    default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
                    ) -> 'StringSymbolValueContext':
        return StringSymbolValueContext(string_sdvs.str_constant(primitive), definition_source, default_restrictions)

    @staticmethod
    def of_reference(
            referenced_symbol_name: str,
            restrictions: ReferenceRestrictions = reference_restrictions.is_any_data_type(),
            definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
            default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
    ) -> 'StringSymbolValueContext':
        return StringSymbolValueContext.of_sdv(string_sdv_of_single_symbol_reference(referenced_symbol_name,
                                                                                     restrictions),
                                               definition_source,
                                               default_restrictions)

    @staticmethod
    def of_arbitrary_value() -> 'StringSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.STRING

    @property
    def assert_equals_sdv(self) -> ValueAssertion[SymbolDependentValue]:
        return asrt_value.equals_string_sdv(self.sdv)

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(symbol_name, self._default_restrictions)

    @staticmethod
    def reference_assertion__string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_string_made_up_of_just_strings(symbol_name)

    @staticmethod
    def usage_assertion__string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolUsage]:
        return is_reference_to_string_made_up_of_just_strings__usage(symbol_name)

    @staticmethod
    def reference_restriction__path_or_string(accepted_relativities: PathRelativityVariants
                                              ) -> ReferenceRestrictions:
        return parse_path.path_or_string_reference_restrictions(accepted_relativities)

    @staticmethod
    def reference_assertion__path_or_string(symbol_name: str,
                                            accepted_relativities: PathRelativityVariants,
                                            ) -> ValueAssertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            asrt_rest.equals_data_type_reference_restrictions(
                parse_path.path_or_string_reference_restrictions(
                    accepted_relativities)
            )
        )

    @staticmethod
    def usage_assertion__path_or_string(symbol_name: str,
                                        accepted_relativities: PathRelativityVariants,
                                        ) -> ValueAssertion[SymbolUsage]:
        return symbol_usage_equals_data_type_symbol_reference(
            SymbolReference(symbol_name,
                            StringSymbolValueContext.reference_restriction__path_or_string(accepted_relativities))
        )

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING


class StringSymbolContext(DataTypeSymbolContext[StringSdv]):
    def __init__(self,
                 name: str,
                 value: StringSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: StringSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
               ) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolValueContext.of_sdv(sdv, definition_source, default_restrictions)
        )

    @staticmethod
    def of_constant(name: str,
                    primitive: str,
                    definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                    default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
                    ) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolValueContext.of_constant(primitive, definition_source, default_restrictions)
        )

    @staticmethod
    def of_reference(
            name: str,
            referenced_symbol_name: str,
            restrictions: ReferenceRestrictions = reference_restrictions.is_any_data_type(),
            definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
            default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
    ) -> 'StringSymbolContext':
        return StringSymbolContext(name,
                                   StringSymbolValueContext.of_reference(referenced_symbol_name,
                                                                         restrictions,
                                                                         definition_source,
                                                                         default_restrictions)
                                   )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'StringSymbolContext':
        return StringSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> StringSymbolValueContext:
        return self._value

    @property
    def argument(self) -> StringMatcherArg:
        return args.SymbolReferenceWReferenceSyntax(self.name)

    def reference__path_or_string(self, accepted_relativities: PathRelativityVariants) -> SymbolReference:
        return SymbolReference(self.name,
                               StringSymbolValueContext.reference_restriction__path_or_string(accepted_relativities))

    @property
    def reference_assertion__string_made_up_of_just_strings(self) -> ValueAssertion[SymbolReference]:
        return StringSymbolValueContext.reference_assertion__string_made_up_of_just_strings(self.name)

    @property
    def usage_assertion__string_made_up_of_just_strings(self) -> ValueAssertion[SymbolUsage]:
        return StringSymbolValueContext.usage_assertion__string_made_up_of_just_strings(self.name)

    @property
    def reference_assertion__path_component(self) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference__ref(
            asrt.equals(self.name),
            asrt_rest.equals_data_type_reference_restrictions(parse_path.PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
        )

    @property
    def usage_assertion__path_component(self) -> ValueAssertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference(
            asrt.equals(self.name),
            asrt_rest.equals_data_type_reference_restrictions(parse_path.PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
        )

    def reference_assertion__path_or_string(self, accepted_relativities: PathRelativityVariants
                                            ) -> ValueAssertion[SymbolReference]:
        return StringSymbolValueContext.reference_assertion__path_or_string(self.name, accepted_relativities)

    def usage_assertion__path_or_string(self, accepted_relativities: PathRelativityVariants
                                        ) -> ValueAssertion[SymbolUsage]:
        return StringSymbolValueContext.usage_assertion__path_or_string(self.name, accepted_relativities)


class StringConstantSymbolContext(StringSymbolContext):
    def __init__(self,
                 name: str,
                 constant: str = 'string value',
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
                 ):
        super().__init__(name,
                         StringSymbolValueContext.of_constant(constant, definition_source, default_restrictions))
        self._constant = constant

    @property
    def str_value(self) -> str:
        return self._constant


class StringIntConstantSymbolContext(StringConstantSymbolContext):
    def __init__(self,
                 name: str,
                 constant: int,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 default_restrictions: ValueAssertion[ReferenceRestrictions] = asrt_rest.is_string_value_restriction,
                 ):
        super().__init__(name, str(constant), definition_source, default_restrictions)
        self._int_constant = constant

    @property
    def int_value(self) -> int:
        return self._int_constant


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringSymbolValueContext.of_constant('arbitrary value')
