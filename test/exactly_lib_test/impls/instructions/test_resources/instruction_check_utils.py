import unittest

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.result import sh, svh
from exactly_lib_test.impls.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class InstructionExecutionBase:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementWithSds,
                 expectation: ExpectationBase):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def _check_instruction(self, expected_class: type, instruction):
        validation = asrt.IsInstance(expected_class,
                                     'The instruction must be an instance of ' + str(expected_class))
        validation.apply(self.put, instruction)

    def _check_result_of_main__sh(self, actual):
        validation = asrt.IsInstance(sh.SuccessOrHardError,
                                     'The result from main must be an instance of ' + str(sh.SuccessOrHardError))
        validation.apply(self.put, actual)

    def _check_result_of_validate_pre_sds(self, actual):
        self._check_instance_and('Result of validate/pre-SDS',
                                 svh.SuccessOrValidationErrorOrHardError,
                                 self.expectation.validation_pre_sds,
                                 actual)

    def _check_main_side_effects_on_sds(self, tcds: TestCaseDs):
        self.expectation.main_side_effects_on_sds.apply(self.put,
                                                        tcds.sds,
                                                        asrt.MessageBuilder('main side effects on SDS'))

    def _check_side_effects_on_tcds(self, tcds: TestCaseDs):
        self.expectation.main_side_effects_on_tcds.apply(self.put,
                                                         tcds,
                                                         asrt.MessageBuilder('side effects on HomeAndSds'))

    def _check_instance_and(self,
                            object_name: str,
                            expected_class: type,
                            additional: Assertion,
                            actual):
        asrt.And([
            asrt.IsInstance(expected_class),
            additional
        ]).apply(self.put, actual, asrt.MessageBuilder(object_name))
