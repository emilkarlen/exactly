import pathlib
import types
import unittest

from exactly_lib.execution.impl.single_instruction_executor import execute_element, \
    ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum, SingleInstructionExecutionFailure
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.section_document.source_location import FileLocationInfo
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util import line_source
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources.elements import new_ls_from_line
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as asrt_failure_details
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


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

    def apply(self, instruction: TestCaseInstruction) -> PartialInstructionControlledFailureInfo:
        self.__do_record()
        return None


class FailingExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 do_record: types.FunctionType,
                 ret_val: PartialInstructionControlledFailureInfo):
        self.__do_record = do_record
        self.__ret_val = ret_val

    def apply(self, instruction: TestCaseInstruction) -> PartialInstructionControlledFailureInfo:
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

    def apply(self, instruction: TestCaseInstruction) -> PartialInstructionControlledFailureInfo:
        self.__do_record()
        raise self.__exception


class Test(unittest.TestCase):
    def test_when_the_executor_is_successful_than_the_result_should_be_success(self):
        element = new_dummy_instruction_element()
        result = execute_element(SuccessfulExecutor(NameRecorder().new_function_that_records('s')),
                                 element,
                                 element.instruction_info)
        self.assertIsNone(result)

    def test_when_the_executor_returns__fail__then_this_failure_should_be_returned(self):
        self._executor_that_returns_failure_helper(PartialControlledFailureEnum.FAIL,
                                                   ExecutionFailureStatus.FAIL)

    def test_when_the_executor_returns__hard_error__then_this_failure_should_be_returned(self):
        self._executor_that_returns_failure_helper(PartialControlledFailureEnum.HARD_ERROR,
                                                   ExecutionFailureStatus.HARD_ERROR)

    def test_when_the_executor__raises_exception__then_an_error_should_be_returned(self):
        # ARRANGE #
        element = new_dummy_instruction_element()
        exception = TestException()
        # ACT #
        result = execute_element(
            ExceptionRaisingExecutor(NameRecorder().new_function_that_records('s'),
                                     exception),
            element,
            element.instruction_info)
        # ASSERT #
        self._check_failure_result(ExecutionFailureStatus.IMPLEMENTATION_ERROR,
                                   result,
                                   asrt_failure_details.matches_exception(asrt.equals(exception)))

    def _executor_that_returns_failure_helper(self,
                                              failure_status_of_executor: PartialControlledFailureEnum,
                                              expected_status: ExecutionFailureStatus):
        # ARRANGE #
        element = new_dummy_instruction_element()
        # ACT #
        result = execute_element(
            FailingExecutor(
                NameRecorder().new_function_that_records('s'),
                PartialInstructionControlledFailureInfo(
                    failure_status_of_executor,
                    asrt_text_doc.new_single_string_text_for_test('error message'))
            ),
            element,
            element.instruction_info)
        # ASSERT #
        self._check_failure_result(expected_status,
                                   result,
                                   asrt_failure_details.is_failure_message_of('error message'))

    def _check_failure_result(self,
                              expected_status: ExecutionFailureStatus,
                              result: SingleInstructionExecutionFailure,
                              expected_failure_details: ValueAssertion[FailureDetails]):
        self.assertIsNotNone(result,
                             'Failure information is expected')
        self.assertEqual(result.status,
                         expected_status,
                         'Result status')
        expected_failure_details.apply_with_message(self,
                                                    result.failure_details,
                                                    'failure_details')


def assert_equal_lines(unit_tc: unittest.TestCase,
                       expected: line_source.Line,
                       actual: line_source.Line):
    unit_tc.assertEqual(expected.line_number,
                        actual.line_number,
                        'Source line number')
    unit_tc.assertEqual(expected.text,
                        actual.text,
                        'Source text')


def new_dummy_instruction_element() -> SectionContentElement:
    return SectionContentElementBuilder(FileLocationInfo(pathlib.Path('/'))) \
        .new_instruction(new_ls_from_line(line_source.Line(100, '100')),
                         TestCaseInstruction())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
