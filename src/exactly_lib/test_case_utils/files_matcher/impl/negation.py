from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs


def negation_matcher(matcher_to_negate: FilesMatcherSdv) -> FilesMatcherSdv:
    return FilesMatcherSdv(combinator_sdvs.Negation(matcher_to_negate.matcher))
