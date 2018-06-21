import unittest
from typing import Optional, Type

from exactly_lib.execution.failure_info import FailureInfo, InstructionFailureInfo, PhaseFailureInfo
from exactly_lib.execution.phase_step import PhaseStep, SimplePhaseStep
from exactly_lib.util import line_source
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib_test.test_case.test_resources.phase_assertions import equals_simple_phase_step
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.util.test_resources import failure_details_assertions as asrt_failure_details
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line_sequence


class ExpectedFailure(asrt.ValueAssertion[Optional[FailureInfo]]):

    def apply(self,
              put: unittest.TestCase,
              value: FailureInfo,
              message_builder: MessageBuilder = MessageBuilder()):
        self._assertions(put, value)

    def _assertions(self,
                    unittest_case: unittest.TestCase,
                    actual_failure_info: FailureInfo):
        raise NotImplementedError()


class ExpectedFailureForNoFailure(ExpectedFailure):
    def _assertions(self,
                    unittest_case: unittest.TestCase,
                    actual_failure_info: FailureInfo):
        unittest_case.assertIsNone(actual_failure_info,
                                   'There should be no failure')


class ExpectedFailureForInstructionFailure(ExpectedFailure):
    def __init__(self,
                 phase_step: SimplePhaseStep,
                 source_line: line_source.LineSequence,
                 failure_details: asrt.ValueAssertion[FailureDetails]):
        if not isinstance(phase_step, SimplePhaseStep):
            raise TypeError('must be SimplePhaseStep. Found: ' + str(type(phase_step)))
        self._phase_step = equals_simple_phase_step(phase_step)
        self._source_line = source_line
        self._expected_failure_details = failure_details

    @staticmethod
    def new_with_message(phase_step: SimplePhaseStep,
                         source: line_source.LineSequence,
                         error_message: str) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source,
                                                    asrt_failure_details.is_failure_message_of(error_message))

    @staticmethod
    def new_with_message_assertion(phase_step: SimplePhaseStep,
                                   source_line: line_source.LineSequence,
                                   error_message: asrt.ValueAssertion[str]) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source_line,
                                                    asrt_failure_details.is_failure_message_matching(error_message))

    @staticmethod
    def new_with_phase_and_message_assertion(phase_step: SimplePhaseStep,
                                             error_message: asrt.ValueAssertion[str]
                                             ) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    None,
                                                    asrt_failure_details.is_failure_message_matching(error_message))

    @staticmethod
    def new_with_exception(phase_step: SimplePhaseStep,
                           source_line: line_source.LineSequence,
                           exception_class: Type[Exception]) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source_line,
                                                    asrt_failure_details.is_exception(exception_class))

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: PhaseStep,
                    actual_line: line_source.LineSequence,
                    actual_details: FailureDetails):
        unittest_case.assertIsInstance(phase_step, PhaseStep, 'must be PhaseStep value')
        self._phase_step.apply_with_message(unittest_case,
                                            phase_step.simple,
                                            'phase_step')
        if self._source_line is not None:
            assert_equals_line_sequence(unittest_case,
                                        self._source_line,
                                        actual_line)
        self._expected_failure_details.apply_without_message(unittest_case,
                                                             actual_details)

    def _assertions(self,
                    unittest_case: unittest.TestCase,
                    actual: FailureInfo):
        unittest_case.assertIsNotNone(actual,
                                      'Failure info should be present')
        unittest_case.assertIsInstance(actual, InstructionFailureInfo,
                                       'The failure is expected to be a {}'.format(str(InstructionFailureInfo)))
        assert isinstance(actual, InstructionFailureInfo)
        self.assertions_(unittest_case,
                         actual.phase_step,
                         actual.source_location.location.source,
                         actual.failure_details)


class ExpectedFailureForPhaseFailure(ExpectedFailure):
    def __init__(self,
                 phase_step: SimplePhaseStep,
                 failure_details: asrt.ValueAssertion[FailureDetails]):
        if not isinstance(phase_step, SimplePhaseStep):
            raise TypeError('must be PhaseStep. Found: ' + str(type(phase_step)))
        self._phase_step = equals_simple_phase_step(phase_step)
        self._failure_details = failure_details

    @staticmethod
    def new_with_step(phase_step: SimplePhaseStep) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForPhaseFailure(phase_step,
                                              asrt_failure_details.is_any_failure_message())

    @staticmethod
    def new_with_message(phase_step: SimplePhaseStep,
                         error_message: str) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForPhaseFailure(phase_step,
                                              asrt_failure_details.is_failure_message_of(error_message))

    @staticmethod
    def new_with_exception(phase_step: SimplePhaseStep,
                           exception_class) -> asrt.ValueAssertion[FailureInfo]:
        return ExpectedFailureForPhaseFailure(phase_step,
                                              asrt_failure_details.is_exception(exception_class))

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: SimplePhaseStep,
                    actual_details: FailureDetails):
        self._phase_step.apply_with_message(unittest_case,
                                            phase_step,
                                            'simple_phase_step')
        self._failure_details.apply_with_message(unittest_case,
                                                 actual_details,
                                                 'failure_details')

    def _assertions(self,
                    unittest_case: unittest.TestCase,
                    actual: FailureInfo):
        unittest_case.assertIsNotNone(actual,
                                      'Failure info should be present')
        unittest_case.assertIsInstance(actual, PhaseFailureInfo,
                                       'The failure is expected to be a {}'.format(str(PhaseFailureInfo)))
        assert isinstance(actual, PhaseFailureInfo)
        self.assertions_(unittest_case,
                         actual.phase_step.simple,
                         actual.failure_details)