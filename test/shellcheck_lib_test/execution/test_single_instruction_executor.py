import types
import unittest

from shellcheck_lib.document.model import Instruction, PhaseContentElement, new_instruction_e
from shellcheck_lib.execution.result import FailureDetails, new_failure_details_from_message, \
    PartialResultStatus, \
    new_failure_details_from_exception
from shellcheck_lib.execution.single_instruction_executor import execute_element, ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum, SingleInstructionExecutionFailure
from shellcheck_lib.general import line_source
from shellcheck_lib_test.test_resources.model_utils import new_ls_from_line


class NameRecorder:
    def __init__(self):
        self.__list = []

    @property
    def recorded_elements(self) -> list:
        return self.__list

    def new_function_that_records(self, s: str) -> types.FunctionType:
        return lambda: self.__list.append(s)


class SuccessfulExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 do_record: types.FunctionType):
        self.__do_record = do_record

    def apply(self, instruction: Instruction) -> PartialInstructionControlledFailureInfo:
        self.__do_record()
        return None


class FailingExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 do_record: types.FunctionType,
                 ret_val: PartialInstructionControlledFailureInfo):
        self.__do_record = do_record
        self.__ret_val = ret_val

    def apply(self, instruction: Instruction) -> PartialInstructionControlledFailureInfo:
        self.__do_record()
        return self.__ret_val


class TestException(Exception):
    pass


class ExceptionRaisingExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 do_record: types.FunctionType,
                 exception: Exception):
        self.__do_record = do_record
        self.__exception = exception

    def apply(self, instruction: Instruction) -> PartialInstructionControlledFailureInfo:
        self.__do_record()
        raise self.__exception


class Test(unittest.TestCase):
    def test_when_the_executor_is_successful_than_the_result_should_be_success(self):
        result = execute_element(SuccessfulExecutor(NameRecorder().new_function_that_records('s')),
                                 new_dummy_instruction_element())
        self.assertIsNone(result)

    def test_when_the_executor_returns__fail__then_this_failure_should_be_returned(self):
        self._executor_that_returns_failure_helper(PartialControlledFailureEnum.FAIL,
                                                   PartialResultStatus.FAIL)

    def test_when_the_executor_returns__hard_error__then_this_failure_should_be_returned(self):
        self._executor_that_returns_failure_helper(PartialControlledFailureEnum.HARD_ERROR,
                                                   PartialResultStatus.HARD_ERROR)

    def test_when_the_executor__raises_exception__then_an_error_should_be_returned(self):
        element = new_dummy_instruction_element()
        exception = TestException()
        result = execute_element(
            ExceptionRaisingExecutor(NameRecorder().new_function_that_records('s'),
                                     exception),
            element)
        self._check_failure_result(PartialResultStatus.IMPLEMENTATION_ERROR,
                                   result,
                                   new_failure_details_from_exception(exception))

    def _executor_that_returns_failure_helper(self,
                                              failure_status_of_executor: PartialControlledFailureEnum,
                                              expected_status: PartialResultStatus):
        element = new_dummy_instruction_element()
        result = execute_element(
            FailingExecutor(NameRecorder().new_function_that_records('s'),
                            PartialInstructionControlledFailureInfo(failure_status_of_executor,
                                                                    'error message')),
            element)
        self._check_failure_result(expected_status,
                                   result,
                                   new_failure_details_from_message('error message'))

    def _check_failure_result(self,
                              expected_status: PartialResultStatus,
                              result: SingleInstructionExecutionFailure,
                              expected_failure_details: FailureDetails):
        self.assertIsNotNone(result,
                             'Failure information is expected')
        self.assertEqual(result.status,
                         expected_status,
                         'Result status')
        assert_equal_failure_details(self,
                                     expected_failure_details,
                                     result.failure_details)


def assert_equal_failure_details(unit_tc: unittest.TestCase,
                                 expected: FailureDetails,
                                 actual: FailureDetails):
    if expected.is_error_message:
        unit_tc.assertTrue(actual.is_error_message,
                           'An error message is expected')
        unit_tc.assertEqual(expected.failure_message,
                            actual.failure_message,
                            'The failure message should be the expected')
    else:
        unit_tc.assertFalse(actual.is_error_message,
                            'An exception is expected')
        unit_tc.assertEqual(expected.exception,
                            actual.exception,
                            'The exception should be the expected')


def assert_equal_lines(unit_tc: unittest.TestCase,
                       expected: line_source.Line,
                       actual: line_source.Line):
    unit_tc.assertEqual(expected.line_number,
                        actual.line_number,
                        'Source line number')
    unit_tc.assertEqual(expected.text,
                        actual.text,
                        'Source text')


def new_dummy_instruction_element() -> PhaseContentElement:
    return new_instruction_e(new_ls_from_line(line_source.Line(100, '100')),
                             Instruction())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
