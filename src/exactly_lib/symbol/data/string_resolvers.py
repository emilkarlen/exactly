"""
Import qualified!
"""

from typing import Iterable

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.impl import string_resolver_impls as _impl
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver, StringResolver
from exactly_lib.type_system.data.concrete_string_values import StrValueTransformer


def str_fragment(constant: str) -> StringFragmentResolver:
    return _impl.ConstantStringFragmentResolver(constant)


def symbol_fragment(symbol_reference: su.SymbolReference) -> StringFragmentResolver:
    return _impl.SymbolStringFragmentResolver(symbol_reference)


def file_ref_fragment(file_ref: FileRefResolver) -> StringFragmentResolver:
    return _impl.FileRefAsStringFragmentResolver(file_ref)


def list_fragment(list_resolver: ListResolver) -> StringFragmentResolver:
    return _impl.ListAsStringFragmentResolver(list_resolver)


def transformed_fragment(fragment: StringFragmentResolver,
                         transformer: StrValueTransformer) -> StringFragmentResolver:
    return _impl.TransformedStringFragmentResolver(fragment, transformer)


def str_constant(string: str) -> StringResolver:
    return StringResolver((str_fragment(string),))


def symbol_reference(symbol_ref: su.SymbolReference) -> StringResolver:
    return StringResolver((symbol_fragment(symbol_ref),))


def from_file_ref_resolver(file_ref: FileRefResolver) -> StringResolver:
    return StringResolver((file_ref_fragment(file_ref),))


def from_list_resolver(list_resolver: ListResolver) -> StringResolver:
    return StringResolver((list_fragment(list_resolver),))


def from_fragments(fragments: Iterable[StringFragmentResolver]) -> StringResolver:
    return StringResolver(tuple(fragments))
