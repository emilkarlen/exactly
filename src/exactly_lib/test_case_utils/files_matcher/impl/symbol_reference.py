from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.type_system.value_type import ValueType


def symbol_reference_matcher(name_of_referenced_sdv: str) -> FilesMatcherSdv:
    return FilesMatcherSdv(MatcherReferenceSdv(name_of_referenced_sdv,
                                               ValueType.FILES_MATCHER))
