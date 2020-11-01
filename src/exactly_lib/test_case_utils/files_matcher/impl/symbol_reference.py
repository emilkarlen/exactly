from exactly_lib.symbol.value_type import ValueType
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv


def symbol_reference_matcher(name_of_referenced_sdv: str) -> FilesMatcherSdv:
    return MatcherReferenceSdv(name_of_referenced_sdv,
                               ValueType.FILES_MATCHER)
