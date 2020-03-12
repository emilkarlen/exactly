from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.path_sdv_impls.constant import PathConstantSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType, \
    SpecificPathRelativity
from exactly_lib.test_case_utils.parse.parse_path import path_or_string_reference_restrictions
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolTableValue, SdvSymbolContext
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class PathSymbolTableValue(SymbolTableValue[PathSdv]):
    def __init__(self,
                 sdv: PathSdv,
                 accepted_relativities: PathRelativityVariants,
                 ):
        super().__init__(sdv)
        self._sdtv = sdv
        self._accepted_relativities = accepted_relativities

    @staticmethod
    def of_sdv(sdv: PathSdv,
               accepted_relativities: PathRelativityVariants,
               ) -> 'PathSymbolTableValue':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return PathSymbolTableValue(sdv, accepted_relativities)

    @staticmethod
    def of_ddv(ddv: PathDdv,
               accepted_relativities: PathRelativityVariants,
               ) -> 'PathSymbolTableValue':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return PathSymbolTableValue(PathConstantSdv(ddv), accepted_relativities)

    @property
    def accepted_relativities(self) -> PathRelativityVariants:
        return self._accepted_relativities

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return equals_symbol_reference(
            SymbolReference(symbol_name,
                            path_or_string_reference_restrictions(self._accepted_relativities))
        )


class PathSymbolContext(SdvSymbolContext[PathSdv]):
    def __init__(self,
                 name: str,
                 value: PathSymbolTableValue,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str,
               sdv: PathSdv,
               accepted_relativities: PathRelativityVariants,
               ) -> 'PathSymbolContext':
        return PathSymbolContext(
            name,
            PathSymbolTableValue.of_sdv(sdv, accepted_relativities)
        )

    @staticmethod
    def of_ddv(name: str,
               ddv: PathDdv,
               accepted_relativities: PathRelativityVariants,
               ) -> 'PathSymbolContext':
        return PathSymbolContext(
            name,
            PathSymbolTableValue.of_sdv(PathConstantSdv(ddv),
                                        accepted_relativities)
        )

    @property
    def symbol_table_value(self) -> PathSymbolTableValue:
        return self._value


class PathDdvSymbolContext(PathSymbolContext):
    def __init__(self,
                 name: str,
                 ddv: PathDdv,
                 accepted_relativities: PathRelativityVariants,
                 ):
        super().__init__(name, PathSymbolTableValue.of_sdv(PathConstantSdv(ddv),
                                                           accepted_relativities))
        self._ddv = ddv

    @staticmethod
    def of_rel_option(name: str,
                      relativity: RelOptionType,
                      suffix: str,
                      accepted_relativities: PathRelativityVariants,
                      ) -> 'PathDdvSymbolContext':
        return PathDdvSymbolContext(name,
                                    paths.of_rel_option(relativity,
                                                        paths.constant_path_part(suffix)),
                                    accepted_relativities,
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
