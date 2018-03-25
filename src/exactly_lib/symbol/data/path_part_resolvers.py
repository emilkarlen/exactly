"""
All construction of :class:`PathPartResolver` should be done via this module.

Import qualified!
"""

from exactly_lib.symbol.data.file_ref_resolver import PathPartResolver
from exactly_lib.symbol.data.file_ref_resolver_impls import path_part_resolver_impls as _impl
from exactly_lib.symbol.data.string_resolver import StringResolver


def empty() -> PathPartResolver:
    return _impl.PathPartResolverAsNothing()


def from_constant_str(file_name: str) -> PathPartResolver:
    return _impl.PathPartResolverAsFixedPath(file_name)


def from_string(string_resolver: StringResolver) -> PathPartResolver:
    return _impl.PathPartResolverAsStringResolver(string_resolver)
