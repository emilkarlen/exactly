import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib_test.execution.partial_execution.test_resources.recording import validate_symbols_utils
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests(validate_symbols_utils.suite_for(conf)
                     for conf in _configurations())
    return ret_val


class ConfigForSetupValidateSymbols(validate_symbols_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.SETUP,
                         phase_step.SETUP__VALIDATE_SYMBOLS,
                         expected_steps=[phase_step.SETUP__VALIDATE_SYMBOLS])

    def instruction_that_returns(self, return_value: list) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(value_usages=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(value_usages=do_raise(exception))


def _configurations() -> list:
    return [
        ConfigForSetupValidateSymbols(),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
