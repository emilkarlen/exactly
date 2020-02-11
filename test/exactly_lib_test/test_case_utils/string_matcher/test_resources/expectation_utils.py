from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, ParseExpectation, \
    ExecutionExpectation
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    parse_expectation = ParseExpectation(
        symbol_references=conf.symbols.usages_expectation(),
    )
    if conf.exists_pre_sds:
        return Expectation(
            parse_expectation,
            ExecutionExpectation(
                validation=asrt_validation.pre_sds_validation_fails__w_any_msg(),
            ),
        )
    else:
        return Expectation(
            parse_expectation,
            ExecutionExpectation(
                validation=asrt_validation.post_sds_validation_fails__w_any_msg(),
            ),
        )
