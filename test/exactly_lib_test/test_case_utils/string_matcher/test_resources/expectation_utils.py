from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return Expectation(
            validation_pre_sds=matcher_assertions.is_arbitrary_validation_failure(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
    else:
        return Expectation(
            main_result=matcher_assertions.is_arbitrary_matching_failure(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
