from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher


def arbitrary_file_matcher() -> FileMatcher:
    return constant_result(True)


def constant_result(result: bool) -> FileMatcher:
    return constant.MatcherWithConstantResult(result)
