import pathlib
from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType, \
    SpecificPathRelativity
from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.type_val_deps.types.path import references as path_references
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_deps.types.path.path_relativities import ALL_REL_OPTION_VARIANTS
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.path.path_sdv_impls import path_rel_symbol
from exactly_lib.type_val_deps.types.path.path_sdv_impls.constant import PathConstantSdv
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import \
    data_restrictions_assertions as asrt_data_ref_restriction
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_context import DataSymbolValueContext, \
    DataTypeSymbolContext
from exactly_lib_test.type_val_deps.types.path.test_resources import sdv_assertions
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.references import path_reference_restrictions, \
    PathReferenceVariant


class PathSymbolValueContext(DataSymbolValueContext[PathSdv]):
    def __init__(self,
                 sdv: PathSdv,
                 accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
                 ):
        super().__init__(sdv, definition_source)
        self._accepted_relativities = accepted_relativities
        self._default_reference_variant = default_reference_variant

    @staticmethod
    def of_sdv(sdv: PathSdv,
               accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
               ) -> 'PathSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return PathSymbolValueContext(sdv, accepted_relativities, definition_source, default_reference_variant)

    @staticmethod
    def of_ddv(ddv: PathDdv,
               accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
               ) -> 'PathSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return PathSymbolValueContext(PathConstantSdv(ddv),
                                      accepted_relativities,
                                      definition_source,
                                      default_reference_variant)

    @staticmethod
    def of_rel_opt_and_suffix(relativity: RelOptionType,
                              suffix: str,
                              accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'PathSymbolValueContext':
        return PathSymbolValueContext.of_ddv(path_ddvs.of_rel_option(relativity,
                                                                     path_ddvs.constant_path_part(suffix)),
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
                     default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
                     ) -> 'PathSymbolValueContext':
        return PathSymbolValueContext(
            path_rel_symbol.PathSdvRelSymbol(
                path_part_sdvs.empty(),
                SymbolReference(referenced_symbol_name,
                                path_reference_restrictions(accepted_relativities))
            ),
            accepted_relativities,
            definition_source,
            default_reference_variant,
        )

    @staticmethod
    def of_arbitrary_value() -> 'PathSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    @property
    def assert_equals_sdv(self) -> Assertion[SymbolDependentValue]:
        return sdv_assertions.equals_path_sdv(self.sdv)

    @property
    def accepted_relativities(self) -> PathRelativityVariants:
        return self._accepted_relativities

    @property
    def reference_restriction__path_or_string(self) -> WithStrRenderingTypeRestrictions:
        return path_references.path_or_string_reference_restrictions(self._accepted_relativities)

    @property
    def reference_restriction__path(self) -> WithStrRenderingTypeRestrictions:
        return path_reference_restrictions(self.accepted_relativities)

    def reference_assertion__path_or_string(self, symbol_name: str) -> Assertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            asrt_data_ref_restriction.equals__w_str_rendering(
                self.reference_restriction__path_or_string)
        )

    def reference_assertion__path(self, symbol_name: str) -> Assertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            asrt_data_ref_restriction.equals__w_str_rendering(
                self.reference_restriction__path)
        )

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return (
            self.reference_assertion__path_or_string(symbol_name)
            if self._default_reference_variant is PathReferenceVariant.PATH_OR_STRING
            else
            self.reference_assertion__path(symbol_name)
        )


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
    def abstract_syntax(self) -> PathSymbolReferenceAbsStx:
        return PathSymbolReferenceAbsStx(self.name)

    def reference_sdv__path_or_string(self, default_relativity: RelOptionType) -> PathSdv:
        return path_sdvs.reference(self.reference__path_or_string, path_part_sdvs.empty(), default_relativity)

    @property
    def reference__path(self) -> SymbolReference:
        return SymbolReference(self.name, self.value.reference_restriction__path)

    @property
    def reference_assertion__path_or_string(self) -> Assertion[SymbolReference]:
        return self.reference_assertion

    @property
    def reference_assertion__path(self) -> Assertion[SymbolReference]:
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
                 default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
                 ):
        super().__init__(name, PathSymbolValueContext.of_sdv(PathConstantSdv(ddv),
                                                             accepted_relativities,
                                                             definition_source,
                                                             default_reference_variant))
        self._ddv = ddv

    @staticmethod
    def of_no_suffix(name: str,
                     relativity: RelOptionType,
                     accepted_relativities: PathRelativityVariants = ALL_REL_OPTION_VARIANTS,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
                     ) -> 'PathDdvSymbolContext':
        return PathDdvSymbolContext(
            name,
            path_ddvs.of_rel_option(relativity,
                                    path_ddvs.empty_path_part()),
            accepted_relativities,
            definition_source,
            default_reference_variant,
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
                 default_reference_variant: PathReferenceVariant = PathReferenceVariant.PATH_OR_STRING,
                 ):
        self._path_part = path_ddvs.constant_path_part(suffix)
        super().__init__(name,
                         path_ddvs.of_rel_option(relativity,
                                                 self._path_part),
                         accepted_relativities,
                         definition_source,
                         default_reference_variant)
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
