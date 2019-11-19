"""
All construction of :class:`PathPartResolver` should be done via this module.

Import qualified!
"""

from exactly_lib.symbol.data.path_sdv import PathPartSdv
from exactly_lib.symbol.data.path_sdv_impls import path_part_sdvs as _impl
from exactly_lib.symbol.data.string_sdv import StringSdv


def empty() -> PathPartSdv:
    return _impl.PathPartSdvAsNothing()


def from_constant_str(file_name: str) -> PathPartSdv:
    return _impl.PathPartSdvAsConstantPath(file_name)


def from_string(string_sdv: StringSdv) -> PathPartSdv:
    return _impl.PathPartSdvAsStringSdv(string_sdv)
