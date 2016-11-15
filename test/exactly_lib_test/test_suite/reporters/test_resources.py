from pathlib import Path

from exactly_lib.execution import result
from exactly_lib.processing import test_case_processing
from exactly_lib.test_suite import execution
from exactly_lib.test_suite.execution import SuitesExecutor
from exactly_lib.test_suite.reporters import junit as sut
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.test_resources.execution_utils import TestCaseProcessorThatGivesConstant, \
    DUMMY_CASE_PROCESSING, full_result_with_failure_info, full_result_without_failure_info


def suite_executor_for_case_processing_that_unconditionally(execution_result: result.FullResult,
                                                            std_output_files: StringStdOutFiles,
                                                            root_file_path: Path) -> SuitesExecutor:
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    case_result = test_case_processing.new_executed(execution_result)
    return execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                    lambda conf: TestCaseProcessorThatGivesConstant(case_result))


FULL_RESULT_XFAIL = full_result_with_failure_info(result.FullResultStatus.XFAIL)
FULL_RESULT_XPASS = full_result_without_failure_info(result.FullResultStatus.XPASS)
FULL_RESULT_HARD_ERROR = full_result_with_failure_info(result.FullResultStatus.HARD_ERROR)
FULL_RESULT_VALIDATE = full_result_with_failure_info(result.FullResultStatus.VALIDATE)
FULL_RESULT_IMPLEMENTATION_ERROR = full_result_with_failure_info(result.FullResultStatus.IMPLEMENTATION_ERROR)
