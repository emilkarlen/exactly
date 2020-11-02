from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation, expectation
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_case.result.test_resources import svh_assertions, pfh_assertions


def expectation_that_file_for_actual_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return Expectation(
            validation_pre_sds=svh_assertions.is_validation_error(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
    else:
        return Expectation(
            main_result=pfh_assertions.is_hard_error__with_arbitrary_message(),
            symbol_usages=conf.symbols.usages_expectation(),
        )


def expectation_that_file_for_expected_contents_is_invalid(conf: RelativityOptionConfiguration) -> Expectation:
    if conf.exists_pre_sds:
        return expectation(
            validation=validation.pre_sds_validation_fails__svh(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
    else:
        return expectation(
            main_result=pfh_assertions.is_hard_error__with_arbitrary_message(),
            symbol_usages=conf.symbols.usages_expectation(),
        )
