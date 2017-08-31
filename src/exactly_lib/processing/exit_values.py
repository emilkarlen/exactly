from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.processing import test_case_processing as processing

NO_EXECUTION_EXIT_CODE = 3


def from_full_result(result: FullResultStatus) -> ExitValue:
    return ExitValue(result.value,
                     result.name)


def from_access_error(result: processing.AccessErrorType) -> ExitValue:
    return ExitValue(NO_EXECUTION_EXIT_CODE,
                     result.name)


def from_result(result: processing.Result) -> ExitValue:
    if result.status is processing.Status.EXECUTED:
        return from_full_result(result.execution_result.status)
    elif result.status is processing.Status.ACCESS_ERROR:
        return from_access_error(result.access_error_type)
    else:
        return EXECUTION__IMPLEMENTATION_ERROR


NO_EXECUTION__FILE_ACCESS_ERROR = from_access_error(processing.AccessErrorType.FILE_ACCESS_ERROR)

NO_EXECUTION__PRE_PROCESS_ERROR = from_access_error(processing.AccessErrorType.PRE_PROCESS_ERROR)

NO_EXECUTION__SYNTAX_ERROR = from_access_error(processing.AccessErrorType.SYNTAX_ERROR)

EXECUTION__PASS = from_full_result(FullResultStatus.PASS)

EXECUTION__VALIDATE = from_full_result(FullResultStatus.VALIDATE)

EXECUTION__FAIL = from_full_result(FullResultStatus.FAIL)

EXECUTION__SKIPPED = from_full_result(FullResultStatus.SKIPPED)

EXECUTION__XFAIL = from_full_result(FullResultStatus.XFAIL)

EXECUTION__XPASS = from_full_result(FullResultStatus.XPASS)

EXECUTION__HARD_ERROR = from_full_result(FullResultStatus.HARD_ERROR)

EXECUTION__IMPLEMENTATION_ERROR = from_full_result(FullResultStatus.IMPLEMENTATION_ERROR)

ALL_EXIT_VALUES = [
    NO_EXECUTION__FILE_ACCESS_ERROR,
    NO_EXECUTION__PRE_PROCESS_ERROR,
    NO_EXECUTION__SYNTAX_ERROR,
    EXECUTION__PASS,
    EXECUTION__VALIDATE,
    EXECUTION__FAIL,
    EXECUTION__SKIPPED,
    EXECUTION__XFAIL,
    EXECUTION__XPASS,
    EXECUTION__HARD_ERROR,
    EXECUTION__IMPLEMENTATION_ERROR,
]
