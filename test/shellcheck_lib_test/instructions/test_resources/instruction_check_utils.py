import unittest

from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from shellcheck_lib_test.instructions.test_resources.arrangements import ArrangementWithEds
from shellcheck_lib_test.instructions.test_resources.expectations import ExpectationBase
from shellcheck_lib_test.test_resources import value_assertion as va


class InstructionExecutionToBeReplacedByVaBase:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementWithEds):
        self.put = put
        self.arrangement = arrangement

    def _check_instruction(self, expected_class: type, instruction):
        validation = va.IsInstance(expected_class,
                                   'The instruction must be an instance of ' + str(expected_class))
        validation.apply(self.put, instruction)

    def _check_result_of_main__sh(self, actual):
        validation = va.IsInstance(sh.SuccessOrHardError,
                                   'The result from main must be an instance of ' + str(sh.SuccessOrHardError))
        validation.apply(self.put, actual)

    def _check_result_of_validate_pre_eds(self, actual):
        va.IsInstance(svh.SuccessOrValidationErrorOrHardError,
                      'Result of validate/pre-eds').apply(self.put, actual)

    def _check_result_of_validate_post_setup(self, actual):
        va.IsInstance(svh.SuccessOrValidationErrorOrHardError,
                      'Result of validate/pre-eds').apply(self.put, actual)


class InstructionExecutionBase:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementWithEds,
                 expectation: ExpectationBase):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def _check_instruction(self, expected_class: type, instruction):
        validation = va.IsInstance(expected_class,
                                   'The instruction must be an instance of ' + str(expected_class))
        validation.apply(self.put, instruction)

    def _check_result_of_validate_pre_eds(self, actual):
        self._check_instance_and('Result of validate/pre-EDS',
                                 svh.SuccessOrValidationErrorOrHardError,
                                 self.expectation.validation_pre_eds,
                                 actual)

    def _check_main_side_effects_on_files(self, home_and_eds: HomeAndEds):
        self.expectation.main_side_effects_on_files.apply(self.put,
                                                          home_and_eds.eds,
                                                          va.MessageBuilder('main side effects on EDS'))

    def _check_side_effects_on_home_and_eds(self, home_and_eds: HomeAndEds):
        self.expectation.side_effects_check.apply(self.put,
                                                  home_and_eds,
                                                  va.MessageBuilder('side effects on HomeAndEds'))

    def _check_instance_and(self,
                            object_name: str,
                            expected_class: type,
                            additional: va.ValueAssertion,
                            actual):
        va.And([
            va.IsInstance(expected_class),
            additional
        ]).apply(self.put, actual, va.MessageBuilder(object_name))
