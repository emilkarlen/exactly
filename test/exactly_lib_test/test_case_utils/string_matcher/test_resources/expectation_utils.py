from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return Expectation(
            validation_pre_sds=integration_check.arbitrary_validation_failure(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
    else:
        return Expectation(
            main_result=integration_check.arbitrary_matching_failure(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
