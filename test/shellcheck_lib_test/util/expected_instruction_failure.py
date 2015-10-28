import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib_test.document.test_resources import assert_equals_line
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib_test.util.assert_utils import assertion_message
from shellcheck_lib.execution.result import InstructionFailureInfo, FailureDetails, \
    FullResultStatus, FullResult, FailureInfo, PhaseFailureInfo


class ExpectedFailureDetails(tuple):
    def __new__(cls,
                error_message_or_none: str,
                exception_class_or_none):
        return tuple.__new__(cls, (error_message_or_none,
                                   exception_class_or_none))

    @property
    def error_message_or_none(self) -> str:
        return self[0]

    @property
    def exception_class_or_none(self):
        return self[1]

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual: FailureDetails,
                   message_header: str=None):
        if self.error_message_or_none is None and self.exception_class_or_none is None:
            unittest_case.assertIsNone(actual,
                                       message_header)
        elif self.error_message_or_none is not None:
            unittest_case.assertEqual(self.error_message_or_none,
                                      actual.failure_message,
                                      assertion_message('failure message', message_header))
        else:
            unittest_case.assertIsInstance(actual.exception,
                                           self.exception_class_or_none,
                                           assertion_message('exception class', message_header))


def new_expected_failure_message(msg: str):
    return ExpectedFailureDetails(msg, None)


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
                source_line: line_source.Line,
                error_message_or_none: str,
                exception_class_or_none):
        return tuple.__new__(cls, (phase_step,
                                   source_line,
                                   ExpectedFailureDetails(error_message_or_none,
                                                          exception_class_or_none)))

    @staticmethod
    def new_with_message(phase_step: PhaseStep,
                         source_line: line_source.Line,
                         error_message: str):
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source_line,
                                                    error_message,
                                                    None)

    @staticmethod
    def new_with_exception(phase_step: PhaseStep,
                           source_line: line_source.Line,
                           exception_class):
        return ExpectedFailureForInstructionFailure(phase_step,
                                                    source_line,
                                                    None,
                                                    exception_class)

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: PhaseStep,
                    actual_line: line_source.Line,
                    actual_details: FailureDetails):
        unittest_case.assertEqual(self.phase_step.phase,
                                  phase_step.phase,
                                  'Phase')
        unittest_case.assertEqual(self.phase_step.step,
                                  phase_step.step,
                                  'Step')
        assert_equals_line(unittest_case,
                           self.source_line,
                           actual_line)
        self.expected_instruction_failure.assertions(unittest_case,
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
                         actual.source_line,
                         actual.failure_details)

    @property
    def phase_step(self) -> PhaseStep:
        return self[0]

    @property
    def source_line(self) -> line_source.Line:
        return self[1]

    @property
    def expected_instruction_failure(self) -> ExpectedFailureDetails:
        return self[2]


class ExpectedFailureForPhaseFailure(ExpectedFailure, tuple):
    def __new__(cls,
                phase_step: PhaseStep,
                error_message_or_none: str,
                exception_class_or_none):
        return tuple.__new__(cls, (phase_step,
                                   ExpectedFailureDetails(error_message_or_none,
                                                          exception_class_or_none)))

    @staticmethod
    def new_with_message(phase_step: PhaseStep,
                         error_message: str):
        return ExpectedFailureForPhaseFailure(phase_step,
                                              error_message,
                                              None)

    @staticmethod
    def new_with_exception(phase_step: PhaseStep,
                           exception_class):
        return ExpectedFailureForPhaseFailure(phase_step,
                                              None,
                                              exception_class)

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: PhaseStep,
                    actual_details: FailureDetails):
        unittest_case.assertEqual(self.phase_step.phase,
                                  phase_step.phase,
                                  'Phase')
        unittest_case.assertEqual(self.phase_step.step,
                                  phase_step.step,
                                  'Step')
        self.expected_instruction_failure.assertions(unittest_case,
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
                         actual.phase_step,
                         actual.failure_details)

    @property
    def phase_step(self) -> PhaseStep:
        return self[0]

    @property
    def source_line(self) -> line_source.Line:
        return self[1]

    @property
    def expected_instruction_failure(self) -> ExpectedFailureDetails:
        return self[2]
