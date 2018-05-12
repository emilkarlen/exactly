from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution.result import FullResultStatus
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


def _for_full_result(result: FullResultStatus, color: ForegroundColor) -> ExitValue:
    return ExitValue(result.value,
                     result.name,
                     color)


_FOR_FULL_RESULT = {
    FullResultStatus.PASS: _for_full_result(FullResultStatus.PASS, ForegroundColor.GREEN),
    FullResultStatus.VALIDATE: _for_full_result(FullResultStatus.VALIDATE, ForegroundColor.YELLOW),
    FullResultStatus.FAIL: _for_full_result(FullResultStatus.FAIL, ForegroundColor.RED),
    FullResultStatus.SKIPPED: _for_full_result(FullResultStatus.SKIPPED, ForegroundColor.CYAN),
    FullResultStatus.XFAIL: _for_full_result(FullResultStatus.XFAIL, ForegroundColor.CYAN),
    FullResultStatus.XPASS: _for_full_result(FullResultStatus.XPASS, ForegroundColor.RED),
    FullResultStatus.HARD_ERROR: _for_full_result(FullResultStatus.HARD_ERROR, ForegroundColor.PURPLE),
    FullResultStatus.IMPLEMENTATION_ERROR: _for_full_result(FullResultStatus.IMPLEMENTATION_ERROR,
                                                            ForegroundColor.PURPLE),
}


def from_full_result(status: FullResultStatus) -> ExitValue:
    return _FOR_FULL_RESULT[status]


EXECUTION__PASS = from_full_result(FullResultStatus.PASS)
EXECUTION__VALIDATE = from_full_result(FullResultStatus.VALIDATE)
EXECUTION__FAIL = from_full_result(FullResultStatus.FAIL)
EXECUTION__SKIPPED = from_full_result(FullResultStatus.SKIPPED)
EXECUTION__XFAIL = from_full_result(FullResultStatus.XFAIL)
EXECUTION__XPASS = from_full_result(FullResultStatus.XPASS)
EXECUTION__HARD_ERROR = from_full_result(FullResultStatus.HARD_ERROR)
EXECUTION__IMPLEMENTATION_ERROR = from_full_result(FullResultStatus.IMPLEMENTATION_ERROR)

ALL_EXIT_VALUES = ([
                       NO_EXECUTION__FILE_ACCESS_ERROR,
                       NO_EXECUTION__PRE_PROCESS_ERROR,
                       NO_EXECUTION__SYNTAX_ERROR,
                   ] +
                   list(_FOR_FULL_RESULT.values()))
