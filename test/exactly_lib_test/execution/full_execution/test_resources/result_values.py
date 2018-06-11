from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib_test.test_suite.test_resources.execution_utils import full_result_with_failure_info, \
    full_result_without_failure_info

FULL_RESULT_XFAIL = full_result_with_failure_info(FullExeResultStatus.XFAIL)
FULL_RESULT_XPASS = full_result_without_failure_info(FullExeResultStatus.XPASS)
FULL_RESULT_HARD_ERROR = full_result_with_failure_info(
    FullExeResultStatus.HARD_ERROR)
FULL_RESULT_VALIDATE = full_result_with_failure_info(
    FullExeResultStatus.VALIDATION_ERROR)
FULL_RESULT_IMPLEMENTATION_ERROR = full_result_with_failure_info(
    FullExeResultStatus.IMPLEMENTATION_ERROR)
