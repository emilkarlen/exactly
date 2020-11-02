from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher


def file_matcher_constant_sdv(primitive: FileMatcher) -> FileMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(primitive)


def new_reference(name: str) -> FileMatcherSdv:
    return MatcherReferenceSdv(name, ValueType.FILE_MATCHER)
