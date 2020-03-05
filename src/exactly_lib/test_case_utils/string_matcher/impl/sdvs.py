from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.util.logic_types import ExpectationType


def new_maybe_negated(matcher: GenericStringMatcherSdv,
                      expectation_type: ExpectationType) -> GenericStringMatcherSdv:
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return matcher
