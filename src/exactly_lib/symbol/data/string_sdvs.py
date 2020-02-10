"""
Import qualified!
"""

from typing import Iterable

from exactly_lib.symbol.data.impl import string_sdv_impls as _impl
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringFragmentSdv, StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.data.concrete_strings import StrValueTransformer


def str_fragment(constant: str) -> StringFragmentSdv:
    return _impl.ConstantStringFragmentSdv(constant)


def symbol_fragment(symbol_reference: SymbolReference) -> StringFragmentSdv:
    return _impl.SymbolStringFragmentSdv(symbol_reference)


def path_fragment(path: PathSdv) -> StringFragmentSdv:
    return _impl.PathAsStringFragmentSdv(path)


def list_fragment(list_sdv: ListSdv) -> StringFragmentSdv:
    return _impl.ListAsStringFragmentSdv(list_sdv)


def transformed_fragment(fragment: StringFragmentSdv,
                         transformer: StrValueTransformer) -> StringFragmentSdv:
    return _impl.TransformedStringFragmentSdv(fragment, transformer)


def str_constant(string: str) -> StringSdv:
    return StringSdv((str_fragment(string),))


def symbol_reference(symbol_ref: SymbolReference) -> StringSdv:
    return StringSdv((symbol_fragment(symbol_ref),))


def from_path_sdv(path: PathSdv) -> StringSdv:
    return StringSdv((path_fragment(path),))


def from_list_sdv(list_sdv: ListSdv) -> StringSdv:
    return StringSdv((list_fragment(list_sdv),))


def from_fragments(fragments: Iterable[StringFragmentSdv]) -> StringSdv:
    return StringSdv(tuple(fragments))
