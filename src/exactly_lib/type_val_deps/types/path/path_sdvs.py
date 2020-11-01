"""
All construction of :class:`PathResolver` should be done via this module.

Import qualified!
"""
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs import relativity_root
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv, PathPartSdv
from exactly_lib.type_val_deps.types.path.path_sdv_impls import constant as _constant, path_rel_symbol as _with_symbol, \
    path_from_symbol_reference as _from_symbol_reference


def constant(value: PathDdv) -> PathSdv:
    return _constant.PathConstantSdv(value)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPartDdv = path_ddvs.empty_path_part()) -> PathSdv:
    return constant(path_ddvs.of_rel_option(rel_option, path_suffix))


def of_rel_option_with_const_file_name(rel_option: relativity_root.RelOptionType,
                                       file_name: str) -> PathSdv:
    return constant(path_ddvs.of_rel_option(rel_option, path_ddvs.constant_path_part(file_name)))


def rel_symbol(symbol_reference: SymbolReference, path_suffix: PathPartSdv) -> PathSdv:
    return _with_symbol.PathSdvRelSymbol(path_suffix, symbol_reference)


def reference(path_or_string_symbol: SymbolReference,
              suffix: PathPartSdv,
              default_relativity: RelOptionType,
              ) -> PathSdv:
    return _from_symbol_reference.SdvThatIsIdenticalToReferencedPathOrWithStringValueAsSuffix(
        path_or_string_symbol,
        suffix,
        default_relativity,
    )


def rel_symbol_with_const_file_name(symbol_reference: SymbolReference,
                                    file_name: str) -> PathSdv:
    return _with_symbol.PathSdvRelSymbol(path_part_sdvs.from_constant_str(file_name),
                                         symbol_reference)
