"""
All construction of :class:`ListResolver` should be done via this module.

Import qualified!
"""

import itertools
from typing import Iterable

from exactly_lib.symbol.data import list_resolver as _impl
from exactly_lib.symbol.data import string_resolvers as _string_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver, Element
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.symbol_usage import SymbolReference


def empty() -> ListResolver:
    return from_strings(())


def from_elements(elements: Iterable[Element]) -> ListResolver:
    return ListResolver(elements)


def from_strings(elements: Iterable[StringResolver]) -> ListResolver:
    return ListResolver([string_element(element)
                         for element in elements])


def from_string(element: StringResolver) -> ListResolver:
    return from_strings([element])


def from_str_constants(str_list: Iterable[str]) -> ListResolver:
    return ListResolver([str_element(e) for e in str_list])


def from_str_constant(constant: str) -> ListResolver:
    return from_str_constants([constant])


def concat(lists: Iterable[ListResolver]) -> ListResolver:
    return ListResolver(itertools.chain.from_iterable([x.elements for x in lists]))


def string_element(string_resolver: StringResolver) -> Element:
    return _impl.StringResolverElement(string_resolver)


def symbol_element(symbol_reference: SymbolReference) -> Element:
    return _impl.SymbolReferenceElement(symbol_reference)


def str_element(s: str) -> Element:
    return string_element(_string_resolvers.str_constant(s))
