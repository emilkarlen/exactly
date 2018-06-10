import unittest

from exactly_lib.execution.failure_info import FailureInfo, InstructionFailureInfo, PhaseFailureInfo
from exactly_lib.execution.full_execution.result import FullResultStatus, FullResult
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep, SimplePhaseStep
from exactly_lib.util import line_source
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line_sequence


class ExpectedFailureDetails(tuple):
    def __new__(cls,
                error_message_or_none: asrt.ValueAssertion,
                exception_class_or_none):
        if error_message_or_none is not None:
            if isinstance(error_message_or_none, str):
                raise TypeError(error_message_or_none)
        return tuple.__new__(cls, (error_message_or_none,
                                   exception_class_or_none))

    @property
    def error_message_or_none(self) -> asrt.ValueAssertion:
        return self[0]

    @property
    def exception_class_or_none(self):
        return self[1]

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual: FailureDetails,
                   message_header: str = None):
        message_builder = asrt.new_message_builder(message_header)
        if self.error_message_or_none is None and self.exception_class_or_none is None:
            unittest_case.assertIsNone(actual,
                                       message_header)
        elif self.error_message_or_none is not None:
            self.error_message_or_none.apply_with_message(unittest_case,
                                                          actual.failure_message,
                                                          message_builder.for_sub_component('failure message'))
        else:
            unittest_case.assertIsInstance(actual.exception,
                                           self.exception_class_or_none,
                                           message_builder.for_sub_component('exception class'))


def new_expected_failure_message(msg: str):
    return ExpectedFailureDetails(asrt.equals(msg), None)


def new_expected_exception(exception_class):
    return ExpectedFailureDetails(None, exception_class)


class ExpectedFailure:
    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: FailureInfo):
        raise NotImplementedError()


class ExpectedStatusAndFailure(tuple):
    def __new__(cls,
                status: FullResultStatus,
                failure: ExpectedFailure):
        return tuple.__new__(cls, (status, failure))

    def assertions(self,
                   utc: unittest.TestCase,
                   actual_status: FullResultStatus,
                   actual_failure_info: FailureInfo):
        utc.assertEqual(self.status,
                        actual_status,
                        'Status')
        self.failure.assertions(utc,
                                actual_failure_info)

    def assertions_on_status_and_failure(self,
                                         utc: unittest.TestCase,
                                         actual_result: FullResult):
        self.assertions(utc,
                        actual_result.status,
                        actual_result.failure_info)

    @property
    def status(self) -> FullResultStatus:
        return self[0]

    @property
    def failure(self) -> ExpectedFailure:
        return self[1]


class ExpectedFailureForNoFailure(ExpectedFailure):
    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: FailureInfo):
        unittest_case.assertIsNone(actual_failure_info,
                                   'There should be no failure')


class ExpectedFailureForInstructionFailure(ExpectedFailure, tuple):
    def __new__(cls,
                phase_step: PhaseStep,
                source_line: line_source.LineSequence,
                error_message_or_none: asrt.ValueAssertion,
                exception_class_or_none):
        return tuple.__new__(cls, (phase_step,
                                   source_line,
                                   ExpectedFailureDetails(error_message_or_none,
                                                          exception_class_or_none)))

    @staticmethod
    def new_with_message(phase_step: PhaseStep,
                         source: line_source.LineSequence,
                         error_message: str):
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source,
                                                    asrt.equals(error_message),
                                                    None)

    @staticmethod
    def new_with_message_assertion(phase_step: PhaseStep,
                                   source_line: line_source.LineSequence,
                                   error_message: asrt.ValueAssertion):
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source_line,
                                                    error_message,
                                                    None)

    @staticmethod
    def new_with_phase_and_message_assertion(phase_step: PhaseStep,
                                             error_message: asrt.ValueAssertion):
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    None,
                                                    error_message,
                                                    None)

    @staticmethod
    def new_with_exception(phase_step: PhaseStep,
                           source_line: line_source.LineSequence,
                           exception_class):
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source_line,
                                                    None,
                                                    exception_class)

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: PhaseStep,
                    actual_line: line_source.LineSequence,
                    actual_details: FailureDetails):
        unittest_case.assertEqual(self.phase_step.phase,
                                  phase_step.phase.the_enum,
                                  'Phase')
        unittest_case.assertEqual(self.phase_step.step,
                                  phase_step.step,
                                  'Step')
        if self.source_line is not None:
            assert_equals_line_sequence(unittest_case,
                                        self.source_line,
                                        actual_line)
        self.expected_failure.assertions(unittest_case,
                                         actual_details)

    def assertions(self,
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

    @property
    def phase_step(self) -> PhaseStep:
        return self[0]

    @property
    def source_line(self) -> line_source.LineSequence:
        return self[1]

    @property
    def expected_failure(self) -> ExpectedFailureDetails:
        return self[2]


class ExpectedFailureForPhaseFailure(ExpectedFailure, tuple):
    def __new__(cls,
                phase_step: PhaseStep,
                error_message_or_none: asrt.ValueAssertion,
                exception_class_or_none):
        return tuple.__new__(cls, (phase_step,
                                   ExpectedFailureDetails(error_message_or_none,
                                                          exception_class_or_none)))

    @staticmethod
    def new_with_step(phase_step: PhaseStep):
        return ExpectedFailureForPhaseFailure(phase_step,
                                              asrt.anything_goes(),
                                              None)

    @staticmethod
    def new_with_message(phase_step: PhaseStep,
                         error_message: str):
        return ExpectedFailureForPhaseFailure(phase_step,
                                              asrt.equals(error_message),
                                              None)

    @staticmethod
    def new_with_exception(phase_step: PhaseStep,
                           exception_class):
        return ExpectedFailureForPhaseFailure(phase_step,
                                              None,
                                              exception_class)

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: SimplePhaseStep,
                    actual_details: FailureDetails):
        unittest_case.assertEqual(self.phase_step.phase,
                                  phase_step.phase,
                                  'Phase')
        unittest_case.assertEqual(self.phase_step.step,
                                  phase_step.step,
                                  'Step')
        self.expected_failure.assertions(unittest_case,
                                         actual_details)

    def assertions(self,
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

    @property
    def phase_step(self) -> PhaseStep:
        return self[0]

    @property
    def expected_failure(self) -> ExpectedFailureDetails:
        return self[1]
