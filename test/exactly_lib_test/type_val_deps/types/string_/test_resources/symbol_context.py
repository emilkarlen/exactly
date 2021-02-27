from typing import Optional

from exactly_lib.impls.types.path import parse_path
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference, ReferenceRestrictions, SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_context import DataSymbolValueContext, \
    DataTypeSymbolContext
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    symbol_usage_equals_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.string_.test_resources import reference_assertions
from exactly_lib_test.type_val_deps.types.string_.test_resources import sdv_assertions as asrt_value
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import NonHereDocStringAbsStx, \
    StringReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.string_sdvs import \
    string_sdv_of_single_symbol_reference


class StringSymbolValueContext(DataSymbolValueContext[StringSdv]):
    def __init__(self,
                 sdv: StringSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
                 ):
        super().__init__(sdv, definition_source)
        self._default_restrictions = default_restrictions

    @staticmethod
    def of_sdv(sdv: StringSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
               ) -> 'StringSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return StringSymbolValueContext(sdv, definition_source, default_restrictions)

    @staticmethod
    def of_constant(primitive: str,
                    definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                    default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
                    ) -> 'StringSymbolValueContext':
        return StringSymbolValueContext(string_sdvs.str_constant(primitive), definition_source, default_restrictions)

    @staticmethod
    def of_reference(
            referenced_symbol_name: str,
            restrictions: ReferenceRestrictions = reference_restrictions.is_any_type_w_str_rendering(),
            definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
            default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
    ) -> 'StringSymbolValueContext':
        return StringSymbolValueContext.of_sdv(string_sdv_of_single_symbol_reference(referenced_symbol_name,
                                                                                     restrictions),
                                               definition_source,
                                               default_restrictions)

    @staticmethod
    def of_arbitrary_value() -> 'StringSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def assert_equals_sdv(self) -> Assertion[SymbolDependentValue]:
        return asrt_value.equals_string_sdv(self.sdv)

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(symbol_name, self._default_restrictions)

    @staticmethod
    def reference_assertion__string__w_all_indirect_refs_are_strings(symbol_name: str) -> Assertion[SymbolReference]:
        return reference_assertions.is_sym_ref_to_string__w_all_indirect_refs_are_strings(symbol_name)

    @staticmethod
    def usage_assertion__string__w_all_indirect_refs_are_strings(symbol_name: str) -> Assertion[SymbolUsage]:
        return reference_assertions.is_sym_ref_to_string__w_all_indirect_refs_are_strings__usage(symbol_name)

    @staticmethod
    def reference_restriction__path_or_string(accepted_relativities: PathRelativityVariants
                                              ) -> ReferenceRestrictions:
        return parse_path.path_or_string_reference_restrictions(accepted_relativities)

    @staticmethod
    def reference_assertion__path_or_string(symbol_name: str,
                                            accepted_relativities: PathRelativityVariants,
                                            ) -> Assertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            asrt_rest.equals__w_str_rendering(
                parse_path.path_or_string_reference_restrictions(
                    accepted_relativities)
            )
        )

    @staticmethod
    def usage_assertion__path_or_string(symbol_name: str,
                                        accepted_relativities: PathRelativityVariants,
                                        ) -> Assertion[SymbolUsage]:
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
               default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
               ) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolValueContext.of_sdv(sdv, definition_source, default_restrictions)
        )

    @staticmethod
    def of_constant(name: str,
                    primitive: str,
                    definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                    default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
                    ) -> 'StringSymbolContext':
        return StringSymbolContext(
            name,
            StringSymbolValueContext.of_constant(primitive, definition_source, default_restrictions)
        )

    @staticmethod
    def of_reference(
            name: str,
            referenced_symbol_name: str,
            restrictions: ReferenceRestrictions = reference_restrictions.is_any_type_w_str_rendering(),
            definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
            default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
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
    def argument(self) -> SymbolReferenceArgument:
        return SymbolReferenceArgument(self.name)

    @property
    def abstract_syntax(self) -> NonHereDocStringAbsStx:
        return StringReferenceAbsStx(self._name)

    def reference__path_or_string(self, accepted_relativities: PathRelativityVariants) -> SymbolReference:
        return SymbolReference(self.name,
                               StringSymbolValueContext.reference_restriction__path_or_string(accepted_relativities))

    @property
    def reference_assertion__string__w_all_indirect_refs_are_strings(self) -> Assertion[SymbolReference]:
        return StringSymbolValueContext.reference_assertion__string__w_all_indirect_refs_are_strings(self.name)

    @property
    def usage_assertion__string__w_all_indirect_refs_are_strings(self) -> Assertion[SymbolUsage]:
        return StringSymbolValueContext.usage_assertion__string__w_all_indirect_refs_are_strings(self.name)

    @property
    def reference_assertion__path_component(self) -> Assertion[SymbolReference]:
        return asrt_sym_usage.matches_reference__ref(
            asrt.equals(self.name),
            asrt_rest.equals__w_str_rendering(
                parse_path.PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
        )

    @property
    def usage_assertion__path_component(self) -> Assertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference(
            asrt.equals(self.name),
            asrt_rest.equals__w_str_rendering(
                parse_path.PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
        )

    def reference_assertion__path_or_string(self, accepted_relativities: PathRelativityVariants
                                            ) -> Assertion[SymbolReference]:
        return StringSymbolValueContext.reference_assertion__path_or_string(self.name, accepted_relativities)

    def usage_assertion__path_or_string(self, accepted_relativities: PathRelativityVariants
                                        ) -> Assertion[SymbolUsage]:
        return StringSymbolValueContext.usage_assertion__path_or_string(self.name, accepted_relativities)


class StringConstantSymbolContext(StringSymbolContext):
    def __init__(self,
                 name: str,
                 constant: str = 'string value',
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
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
                 default_restrictions: Assertion[ReferenceRestrictions] = asrt_rest.is__w_str_rendering(),
                 ):
        super().__init__(name, str(constant), definition_source, default_restrictions)
        self._int_constant = constant

    @property
    def int_value(self) -> int:
        return self._int_constant


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringSymbolValueContext.of_constant('arbitrary value')
