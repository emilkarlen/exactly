import pathlib
from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.data import path_part_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.path_sdv_impls import path_rel_symbol
from exactly_lib.symbol.data.path_sdv_impls.constant import PathConstantSdv
from exactly_lib.symbol.data.restrictions.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect, \
    OrReferenceRestrictions, OrRestrictionPart
from exactly_lib.symbol.data.restrictions.value_restrictions import PathRelativityRestriction
from exactly_lib.symbol.restriction import DataTypeReferenceRestrictions
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType, \
    SpecificPathRelativity
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.test_case_utils.parse.path_relativities import ALL_REL_OPTION_VARIANTS
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.path_part import PathPartDdv
from exactly_lib.type_system.value_type import ValueType, DataValueType
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restrictions import \
    string_made_up_of_just_strings_reference_restrictions
from exactly_lib_test.symbol.data.test_resources import concrete_value_assertions as asrt_value
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbols_setup import DataTypeSymbolContext, \
    DataSymbolValueContext, ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def path_reference_restrictions(accepted_relativities: PathRelativityVariants
                                ) -> DataTypeReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(PathRelativityRestriction(accepted_relativities))


def path_or_string_reference_restrictions(accepted_relativities: PathRelativityVariants
                                          ) -> DataTypeReferenceRestrictions:
    return OrReferenceRestrictions([
        OrRestrictionPart(
            DataValueType.PATH,
            ReferenceRestrictionsOnDirectAndIndirect(PathRelativityRestriction(accepted_relativities))),
        OrRestrictionPart(
            DataValueType.STRING,
            string_made_up_of_just_strings_reference_restrictions()),
    ])


class PathSymbolValueContext(DataSymbolValueContext[PathSdv]):
    def __init__(self,
                 sdv: PathSdv,
                 accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)
        self._accepted_relativities = accepted_relativities

    @staticmethod
    def of_sdv(sdv: PathSdv,
               accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'PathSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return PathSymbolValueContext(sdv, accepted_relativities, definition_source)

    @staticmethod
    def of_ddv(ddv: PathDdv,
               accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'PathSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return PathSymbolValueContext(PathConstantSdv(ddv), accepted_relativities, definition_source)

    @staticmethod
    def of_rel_opt_and_suffix(relativity: RelOptionType,
                              suffix: str,
                              accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'PathSymbolValueContext':
        return PathSymbolValueContext.of_ddv(paths.of_rel_option(relativity,
                                                                 paths.constant_path_part(suffix)),
                                             accepted_relativities,
                                             definition_source)

    @staticmethod
    def of_rel_arbitrary_and_suffix(
            suffix: str,
            accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
            definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
    ) -> 'PathSymbolValueContext':
        return PathSymbolValueContext.of_rel_opt_and_suffix(RelOptionType.REL_ACT,
                                                            suffix,
                                                            accepted_relativities,
                                                            definition_source)

    @staticmethod
    def of_reference(referenced_symbol_name: str,
                     accepted_relativities: PathRelativityVariants,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'PathSymbolValueContext':
        return PathSymbolValueContext(
            path_rel_symbol.PathSdvRelSymbol(
                path_part_sdvs.empty(),
                SymbolReference(referenced_symbol_name,
                                path_reference_restrictions(accepted_relativities))
            ),
            accepted_relativities,
            definition_source,
        )

    @staticmethod
    def of_arbitrary_value() -> 'PathSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.PATH

    @property
    def assert_equals_sdv(self) -> ValueAssertion[SymbolDependentValue]:
        return asrt_value.equals_path_sdv(self.sdv)

    @property
    def accepted_relativities(self) -> PathRelativityVariants:
        return self._accepted_relativities

    @property
    def reference_restriction__path_or_string(self) -> DataTypeReferenceRestrictions:
        return parse_path.path_or_string_reference_restrictions(self._accepted_relativities)

    @property
    def reference_restriction__path(self) -> DataTypeReferenceRestrictions:
        return path_reference_restrictions(self.accepted_relativities)

    def reference_assertion__path_or_string(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            concrete_restriction_assertion.equals_data_type_reference_restrictions(
                self.reference_restriction__path_or_string)
        )

    def reference_assertion__path(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            concrete_restriction_assertion.equals_data_type_reference_restrictions(
                self.reference_restriction__path)
        )

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return self.reference_assertion__path_or_string(symbol_name)


class PathSymbolContext(DataTypeSymbolContext[PathSdv]):
    def __init__(self,
                 name: str,
                 value: PathSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: PathSdv,
               accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'PathSymbolContext':
        return PathSymbolContext(
            name,
            PathSymbolValueContext.of_sdv(sdv, accepted_relativities, definition_source)
        )

    @staticmethod
    def of_ddv(name: str,
               ddv: PathDdv,
               accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'PathSymbolContext':
        return PathSymbolContext(
            name,
            PathSymbolValueContext.of_sdv(PathConstantSdv(ddv),
                                          accepted_relativities,
                                          definition_source)
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'PathSymbolContext':
        return PathSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> PathSymbolValueContext:
        return self._value

    @property
    def reference__path(self) -> SymbolReference:
        return SymbolReference(self.name, self.value.reference_restriction__path)

    @property
    def reference_assertion__path_or_string(self) -> ValueAssertion[SymbolReference]:
        return self.reference_assertion

    @property
    def reference_assertion__path(self) -> ValueAssertion[SymbolReference]:
        return self.value.reference_assertion__path(self.name)

    @property
    def reference__path_or_string(self) -> SymbolReference:
        return SymbolReference(self.name, self.value.reference_restriction__path_or_string)


class PathDdvSymbolContext(PathSymbolContext):
    def __init__(self,
                 name: str,
                 ddv: PathDdv,
                 accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name, PathSymbolValueContext.of_sdv(PathConstantSdv(ddv),
                                                             accepted_relativities,
                                                             definition_source))
        self._ddv = ddv

    @staticmethod
    def of_no_suffix(name: str,
                     relativity: RelOptionType,
                     accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'PathDdvSymbolContext':
        return PathDdvSymbolContext(
            name,
            paths.of_rel_option(relativity,
                                paths.empty_path_part()),
            accepted_relativities,
            definition_source,
        )

    @property
    def ddv(self) -> PathDdv:
        return self._ddv

    @property
    def relativity(self) -> SpecificPathRelativity:
        return self._ddv.relativity()

    @property
    def rel_option_type(self) -> RelOptionType:
        return self.relativity.relativity_type


class ConstantSuffixPathDdvSymbolContext(PathDdvSymbolContext):
    def __init__(self,
                 name: str,
                 relativity: RelOptionType,
                 suffix: str,
                 accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        self._path_part = paths.constant_path_part(suffix)
        super().__init__(name,
                         paths.of_rel_option(relativity,
                                             self._path_part),
                         accepted_relativities,
                         definition_source)
        self._suffix = suffix

    @property
    def path_part(self) -> PathPartDdv:
        return self._path_part

    @property
    def path_suffix(self) -> str:
        return self._suffix

    @property
    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self._suffix)


def arbitrary_path_symbol_context(symbol_name: str) -> ConstantSuffixPathDdvSymbolContext:
    return ConstantSuffixPathDdvSymbolContext(symbol_name, RelOptionType.REL_ACT, 'base-name')


ARBITRARY_SYMBOL_VALUE_CONTEXT = PathSymbolValueContext.of_rel_opt_and_suffix(RelOptionType.REL_ACT,
                                                                              'arbitrary-base-name')
