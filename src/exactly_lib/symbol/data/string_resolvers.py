"""
Import qualified!
"""

from typing import Iterable

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.data.impl import string_resolver_impls as _impl
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver, StringResolver
from exactly_lib.type_system.data.concrete_strings import StrValueTransformer


def str_fragment(constant: str) -> StringFragmentResolver:
    return _impl.ConstantStringFragmentResolver(constant)


def symbol_fragment(symbol_reference: su.SymbolReference) -> StringFragmentResolver:
    return _impl.SymbolStringFragmentResolver(symbol_reference)


def path_fragment(path: PathResolver) -> StringFragmentResolver:
    return _impl.PathAsStringFragmentResolver(path)


def list_fragment(list_resolver: ListResolver) -> StringFragmentResolver:
    return _impl.ListAsStringFragmentResolver(list_resolver)


def transformed_fragment(fragment: StringFragmentResolver,
                         transformer: StrValueTransformer) -> StringFragmentResolver:
    return _impl.TransformedStringFragmentResolver(fragment, transformer)


def str_constant(string: str) -> StringResolver:
    return StringResolver((str_fragment(string),))


def symbol_reference(symbol_ref: su.SymbolReference) -> StringResolver:
    return StringResolver((symbol_fragment(symbol_ref),))


def from_path_resolver(path: PathResolver) -> StringResolver:
    return StringResolver((path_fragment(path),))


def from_list_resolver(list_resolver: ListResolver) -> StringResolver:
    return StringResolver((list_fragment(list_resolver),))


def from_fragments(fragments: Iterable[StringFragmentResolver]) -> StringResolver:
    return StringResolver(tuple(fragments))
