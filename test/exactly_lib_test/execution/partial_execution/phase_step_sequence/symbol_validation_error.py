import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib_test.execution.partial_execution.test_resources.recording import validate_symbols_utils
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.test_resources.actions import do_return, do_raise


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests(validate_symbols_utils.suite_for(conf)
                     for conf in _configurations())
    return ret_val


class ConfigForSetupValidateSymbols(validate_symbols_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.SETUP,
                         phase_step.SETUP__VALIDATE_SYMBOLS,
                         expected_steps_before_failing_instruction=[phase_step.SETUP__VALIDATE_SYMBOLS])

    def instruction_that_returns(self, symbol_usages: list) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(symbol_usages=do_return(symbol_usages))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(symbol_usages=do_raise(exception))


class ConfigForBeforeAssertValidateSymbols(validate_symbols_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.BEFORE_ASSERT,
                         phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                         expected_steps_before_failing_instruction=ALL_RECORDING_INSTRUCTIONS_IN_SETUP +
                                                                   ALL_RECORDING_INSTRUCTIONS_IN_ACT +
                                                                   [phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS])

    def instruction_that_returns(self, symbol_usages: list) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(symbol_usages=do_return(symbol_usages))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(symbol_usages=do_raise(exception))


class ConfigForAssertValidateSymbols(validate_symbols_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ASSERT,
                         phase_step.ASSERT__VALIDATE_SYMBOLS,
                         expected_steps_before_failing_instruction=ALL_RECORDING_INSTRUCTIONS_IN_SETUP +
                                                                   ALL_RECORDING_INSTRUCTIONS_IN_ACT +
                                                                   ALL_RECORDING_INSTRUCTIONS_IN_BEFORE_ASSERT +
                                                                   [phase_step.ASSERT__VALIDATE_SYMBOLS])

    def instruction_that_returns(self, symbol_usages: list) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(symbol_usages=do_return(symbol_usages))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(symbol_usages=do_raise(exception))


class ConfigForCleanuptValidateSymbols(validate_symbols_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.CLEANUP,
                         phase_step.CLEANUP__VALIDATE_SYMBOLS,
                         expected_steps_before_failing_instruction=ALL_RECORDING_INSTRUCTIONS_IN_SETUP +
                                                                   ALL_RECORDING_INSTRUCTIONS_IN_ACT +
                                                                   ALL_RECORDING_INSTRUCTIONS_IN_BEFORE_ASSERT +
                                                                   ALL_RECORDING_INSTRUCTIONS_IN_ASSERT +
                                                                   [phase_step.CLEANUP__VALIDATE_SYMBOLS])

    def instruction_that_returns(self, symbol_usages: list) -> TestCaseInstruction:
        return test.cleanup_phase_instruction_that(symbol_usages=do_return(symbol_usages))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.cleanup_phase_instruction_that(symbol_usages=do_raise(exception))


ALL_RECORDING_INSTRUCTIONS_IN_SETUP = [phase_step.SETUP__VALIDATE_SYMBOLS,
                                       phase_step.SETUP__VALIDATE_SYMBOLS]

ALL_RECORDING_INSTRUCTIONS_IN_ACT = [phase_step.ACT__VALIDATE_SYMBOLS]

ALL_RECORDING_INSTRUCTIONS_IN_BEFORE_ASSERT = [phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                                               phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS]

ALL_RECORDING_INSTRUCTIONS_IN_ASSERT = [phase_step.ASSERT__VALIDATE_SYMBOLS,
                                        phase_step.ASSERT__VALIDATE_SYMBOLS]


def _configurations() -> list:
    return [
        ConfigForSetupValidateSymbols(),
        ConfigForBeforeAssertValidateSymbols(),
        ConfigForAssertValidateSymbols(),
        ConfigForCleanuptValidateSymbols(),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
