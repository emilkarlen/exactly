from shelltest_test.phase_instr.test_resources import assert_equals_line
from shelltest_test.test_resources import assertion_message

__author__ = 'emil'

import unittest
from shelltest.execution.result import InstructionFailureInfo, InstructionFailureDetails
from shelltest.phase_instr import line_source


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
            unittest_case.assertIsInstance(self.exception_class_or_none,
                                           actual.exception,
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
                source_line: line_source.Line,
                error_message_or_none: str,
                exception_class_or_none):
        return tuple.__new__(cls, (source_line,
                                   ExpectedInstructionFailureDetails(error_message_or_none,
                                                                     exception_class_or_none)))

    @staticmethod
    def new_with_message(source_line: line_source.Line,
                         error_message: str):
        return ExpectedInstructionFailureForFailure(source_line,
                                                    error_message,
                                                    None)

    @staticmethod
    def new_with_exception(source_line: line_source.Line,
                           exception_class):
        return ExpectedInstructionFailureForFailure(source_line,
                                                    None,
                                                    exception_class)

    def assertions_(self,
                    unittest_case: unittest.TestCase,
                    actual_line: line_source.Line,
                    actual_details: InstructionFailureDetails):
        assert_equals_line(unittest_case,
                           self.source_line,
                           actual_line)
        self.expected_instruction_failure.assertions(unittest_case,
                                                     actual_details)

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual: InstructionFailureInfo):
        unittest_case.assertIsNone(actual,
                                   'Failure info')
        assert_equals_line(unittest_case,
                           self.source_line,
                           actual.source_line)
        self.expected_instruction_failure.assertions(unittest_case,
                                                     actual.failure_details)

    @property
    def source_line(self) -> line_source.Line:
        return self[0]


    @property
    def expected_instruction_failure(self) -> ExpectedInstructionFailureDetails:
        return self[1]
