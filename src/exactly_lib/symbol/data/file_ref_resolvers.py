"""
All construction of :class:`FileRefResolver` should be done via this module.

Import qualified!
"""
from exactly_lib.symbol.data import path_part_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver, PathPartResolver
from exactly_lib.symbol.data.file_ref_resolver_impls import constant as _constant
from exactly_lib.symbol.data.file_ref_resolver_impls import file_ref_with_symbol as _with_symbol
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.path_part import PathPart


def constant(value: FileRef) -> FileRefResolver:
    return _constant.FileRefConstant(value)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPart = file_refs.empty_path_part()) -> FileRefResolver:
    return constant(file_refs.of_rel_option(rel_option, path_suffix))


def of_rel_option_with_const_file_name(rel_option: relativity_root.RelOptionType,
                                       file_name: str) -> FileRefResolver:
    return constant(file_refs.of_rel_option(rel_option, file_refs.constant_path_part(file_name)))


def rel_symbol(symbol_reference: SymbolReference, path_suffix: PathPartResolver) -> FileRefResolver:
    return _with_symbol.FileRefResolverRelSymbol(path_suffix, symbol_reference)


def rel_symbol_with_const_file_name(symbol_reference: SymbolReference,
                                    file_name: str) -> FileRefResolver:
    return _with_symbol.FileRefResolverRelSymbol(path_part_resolvers.from_constant_str(file_name),
                                                 symbol_reference)
