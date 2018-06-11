from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.processing import test_case_processing as processing
from exactly_lib.util.ansi_terminal_color import ForegroundColor

NO_EXECUTION_EXIT_CODE = 3


def from_access_error(result: processing.AccessErrorType) -> ExitValue:
    return ExitValue(NO_EXECUTION_EXIT_CODE,
                     result.name,
                     ForegroundColor.YELLOW)


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


def _for_full_result(result: FullExeResultStatus, color: ForegroundColor) -> ExitValue:
    return ExitValue(result.value,
                     result.name,
                     color)


_FOR_FULL_RESULT = {
    FullExeResultStatus.PASS: _for_full_result(FullExeResultStatus.PASS, ForegroundColor.GREEN),
    FullExeResultStatus.VALIDATION_ERROR: _for_full_result(FullExeResultStatus.VALIDATION_ERROR,
                                                           ForegroundColor.YELLOW),
    FullExeResultStatus.FAIL: _for_full_result(FullExeResultStatus.FAIL, ForegroundColor.RED),
    FullExeResultStatus.SKIPPED: _for_full_result(FullExeResultStatus.SKIPPED, ForegroundColor.CYAN),
    FullExeResultStatus.XFAIL: _for_full_result(FullExeResultStatus.XFAIL, ForegroundColor.CYAN),
    FullExeResultStatus.XPASS: _for_full_result(FullExeResultStatus.XPASS, ForegroundColor.RED),
    FullExeResultStatus.HARD_ERROR: _for_full_result(FullExeResultStatus.HARD_ERROR, ForegroundColor.PURPLE),
    FullExeResultStatus.IMPLEMENTATION_ERROR: _for_full_result(FullExeResultStatus.IMPLEMENTATION_ERROR,
                                                               ForegroundColor.PURPLE),
}


def from_full_result(status: FullExeResultStatus) -> ExitValue:
    return _FOR_FULL_RESULT[status]


EXECUTION__PASS = from_full_result(FullExeResultStatus.PASS)
EXECUTION__VALIDATION_ERROR = from_full_result(FullExeResultStatus.VALIDATION_ERROR)
EXECUTION__FAIL = from_full_result(FullExeResultStatus.FAIL)
EXECUTION__SKIPPED = from_full_result(FullExeResultStatus.SKIPPED)
EXECUTION__XFAIL = from_full_result(FullExeResultStatus.XFAIL)
EXECUTION__XPASS = from_full_result(FullExeResultStatus.XPASS)
EXECUTION__HARD_ERROR = from_full_result(FullExeResultStatus.HARD_ERROR)
EXECUTION__IMPLEMENTATION_ERROR = from_full_result(FullExeResultStatus.IMPLEMENTATION_ERROR)

ALL_EXIT_VALUES = ([
                       NO_EXECUTION__FILE_ACCESS_ERROR,
                       NO_EXECUTION__PRE_PROCESS_ERROR,
                       NO_EXECUTION__SYNTAX_ERROR,
                   ] +
                   list(_FOR_FULL_RESULT.values()))
