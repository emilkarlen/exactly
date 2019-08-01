from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_actual_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return Expectation(
            validation_pre_sds=svh_assertions.is_validation_error(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
    else:
        return Expectation(
            main_result=pfh_assertions.is_fail__with_arbitrary_message(),
            symbol_usages=conf.symbols.usages_expectation(),
        )


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    return expectation_that_file_for_actual_contents_is_invalid(conf)
