"""
All construction of :class:`PathResolver` should be done via this module.

Import qualified!
"""
from exactly_lib.symbol.data import path_part_resolvers
from exactly_lib.symbol.data.path_resolver import PathResolver, PathPartResolver
from exactly_lib.symbol.data.path_resolver_impls import constant as _constant
from exactly_lib.symbol.data.path_resolver_impls import path_with_symbol as _with_symbol
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.path_part import PathPartDdv


def constant(value: PathDdv) -> PathResolver:
    return _constant.PathConstant(value)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPartDdv = paths.empty_path_part()) -> PathResolver:
    return constant(paths.of_rel_option(rel_option, path_suffix))


def of_rel_option_with_const_file_name(rel_option: relativity_root.RelOptionType,
                                       file_name: str) -> PathResolver:
    return constant(paths.of_rel_option(rel_option, paths.constant_path_part(file_name)))


def rel_symbol(symbol_reference: SymbolReference, path_suffix: PathPartResolver) -> PathResolver:
    return _with_symbol.PathResolverRelSymbol(path_suffix, symbol_reference)


def rel_symbol_with_const_file_name(symbol_reference: SymbolReference,
                                    file_name: str) -> PathResolver:
    return _with_symbol.PathResolverRelSymbol(path_part_resolvers.from_constant_str(file_name),
                                              symbol_reference)
