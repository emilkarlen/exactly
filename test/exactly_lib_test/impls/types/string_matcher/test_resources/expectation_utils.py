from exactly_lib_test.impls.test_resources.validation import validation as asrt_validation
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation, ExecutionExpectation, \
    Expectation
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    parse_expectation = ParseExpectation(
        symbol_references=conf.symbols.usages_expectation(),
    )
    if conf.exists_pre_sds:
        return Expectation(
            parse_expectation,
            ExecutionExpectation(
                validation=asrt_validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
            ),
        )
    else:
        return Expectation(
            parse_expectation,
            ExecutionExpectation(
                validation=asrt_validation.ValidationAssertions.post_sds_fails__w_any_msg(),
            ),
        )
