from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation, expectation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return expectation(
            validation=asrt_validation.pre_sds_validation_fails__w_any_msg(),
            symbol_references=conf.symbols.usages_expectation(),
        )
    else:
        return expectation(
            validation=asrt_validation.post_sds_validation_fails__w_any_msg(),
            symbol_references=conf.symbols.usages_expectation(),
        )
