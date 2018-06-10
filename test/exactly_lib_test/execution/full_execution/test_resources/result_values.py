from exactly_lib.execution.full_execution.result import FullResultStatus
from exactly_lib_test.test_suite.test_resources.execution_utils import full_result_with_failure_info, \
    full_result_without_failure_info

FULL_RESULT_XFAIL = full_result_with_failure_info(FullResultStatus.XFAIL)
FULL_RESULT_XPASS = full_result_without_failure_info(FullResultStatus.XPASS)
FULL_RESULT_HARD_ERROR = full_result_with_failure_info(
    FullResultStatus.HARD_ERROR)
FULL_RESULT_VALIDATE = full_result_with_failure_info(
    FullResultStatus.VALIDATION_ERROR)
FULL_RESULT_IMPLEMENTATION_ERROR = full_result_with_failure_info(
    FullResultStatus.IMPLEMENTATION_ERROR)
