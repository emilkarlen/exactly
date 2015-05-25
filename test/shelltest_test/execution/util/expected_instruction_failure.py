import unittest

from shelltest.execution.phase_step import PhaseStep
from shelltest_test.document.test_resources import assert_equals_line
from shelltest_test.test_resources import assertion_message
from shelltest.execution.result import InstructionFailureInfo, InstructionFailureDetails
from shelltest.general import line_source


class ExpectedInstructionFailureDetails(tuple):
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
                   actual: InstructionFailureDetails,
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
    return ExpectedInstructionFailureDetails(msg, None)


def new_expected_exception(exception_class):
    return ExpectedInstructionFailureDetails(None, exception_class)


class ExpectedInstructionFailureBase:
    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: InstructionFailureInfo):
        raise NotImplementedError()


class ExpectedInstructionFailureForNoFailure(ExpectedInstructionFailureBase):
    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: InstructionFailureInfo):
        unittest_case.assertIsNone(actual_failure_info,
                                   'There should be no failure')


class ExpectedInstructionFailureForFailure(ExpectedInstructionFailureBase, tuple):
    def __new__(cls,
                phase_step: PhaseStep,
                source_line: line_source.Line,
                error_message_or_none: str,
                exception_class_or_none):
        return tuple.__new__(cls, (phase_step,
                                   source_line,
                                   ExpectedInstructionFailureDetails(error_message_or_none,
                                                                     exception_class_or_none)))

    @staticmethod
    def new_with_message(phase_step: PhaseStep,
                         source_line: line_source.Line,
                         error_message: str):
        return ExpectedInstructionFailureForFailure(phase_step,
                                                    source_line,
                                                    error_message,
                                                    None)

    @staticmethod
    def new_with_exception(phase_step: PhaseStep,
                           source_line: line_source.Line,
                           exception_class):
        return ExpectedInstructionFailureForFailure(phase_step,
                                                    source_line,
                                                    None,
                                                    exception_class)

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    phase_step: PhaseStep,
                    actual_line: line_source.Line,
                    actual_details: InstructionFailureDetails):
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
                   actual: InstructionFailureInfo):
        unittest_case.assertIsNotNone(actual,
                                      'Failure info should be present')
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
    def expected_instruction_failure(self) -> ExpectedInstructionFailureDetails:
        return self[2]
