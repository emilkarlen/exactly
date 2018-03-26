"""
All construction of :class:`FileRefResolver` should be done via this module.

Import qualified!
"""

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver, PathPartResolver
from exactly_lib.symbol.data.file_ref_resolver_impls import constant as _constant
from exactly_lib.symbol.data.file_ref_resolver_impls import file_ref_with_symbol as _with_symbol
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.path_part import PathPart


def constant(value: FileRef) -> FileRefResolver:
    return _constant.FileRefConstant(value)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  path_suffix: PathPart = PathPartAsNothing()) -> FileRefResolver:
    return constant(file_refs.of_rel_option(rel_option, path_suffix))


def rel_symbol(symbol_reference2: SymbolReference, path_suffix: PathPartResolver) -> FileRefResolver:
    return _with_symbol.FileRefResolverRelSymbol(path_suffix, symbol_reference2)