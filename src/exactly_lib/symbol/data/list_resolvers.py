import itertools
from typing import Sequence

from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver, string_element
from exactly_lib.symbol.data.string_resolver import StringResolver


def empty() -> ListResolver:
    return from_strings(())


def from_strings(elements: Sequence[StringResolver]) -> ListResolver:
    return ListResolver([string_element(element)
                         for element in elements])


def from_str_constants(str_list: Sequence[str]) -> ListResolver:
    return ListResolver([string_element(
        string_resolvers.string_constant(s))
        for s in str_list])


def concat(lists: Sequence[ListResolver]) -> ListResolver:
    return ListResolver(itertools.chain.from_iterable([x.elements for x in lists]))
