from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.util.logic_types import ExpectationType


def new_maybe_negated(matcher: StringMatcherSdv,
                      expectation_type: ExpectationType) -> StringMatcherSdv:
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return matcher
