from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check, pfh_check
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return Expectation(
            validation_pre_sds=svh_check.is_validation_error(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
    else:
        return Expectation(
            main_result=pfh_check.is_fail(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
