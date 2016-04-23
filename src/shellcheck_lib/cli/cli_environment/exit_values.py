from shellcheck_lib.cli.cli_environment.exit_value import ExitValue
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.test_case_processing import AccessErrorType

NO_EXECUTION_EXIT_CODE = 3


def _from_full_result(result: FullResultStatus) -> ExitValue:
    return ExitValue(result.value,
                     result.name)


def _from_access_error(result: AccessErrorType) -> ExitValue:
    return ExitValue(NO_EXECUTION_EXIT_CODE,
                     result.name)


NO_EXECUTION__FILE_ACCESS_ERROR = _from_access_error(AccessErrorType.FILE_ACCESS_ERROR)

NO_EXECUTION__PRE_PROCESS_ERROR = _from_access_error(AccessErrorType.PRE_PROCESS_ERROR)

NO_EXECUTION__PARSE_ERROR = _from_access_error(AccessErrorType.PARSE_ERROR)

EXECUTION__PASS = _from_full_result(FullResultStatus.PASS)

EXECUTION__VALIDATE = _from_full_result(FullResultStatus.VALIDATE)

EXECUTION__FAIL = _from_full_result(FullResultStatus.FAIL)

EXECUTION__SKIPPED = _from_full_result(FullResultStatus.SKIPPED)

EXECUTION__XFAIL = _from_full_result(FullResultStatus.XFAIL)

EXECUTION__XPASS = _from_full_result(FullResultStatus.XPASS)

EXECUTION__HARD_ERROR = _from_full_result(FullResultStatus.HARD_ERROR)

EXECUTION__IMPLEMENTATION_ERROR = _from_full_result(FullResultStatus.IMPLEMENTATION_ERROR)

ALL_EXIT_VALUES = [
    NO_EXECUTION__FILE_ACCESS_ERROR,
    NO_EXECUTION__PRE_PROCESS_ERROR,
    NO_EXECUTION__PARSE_ERROR,
    EXECUTION__PASS,
    EXECUTION__VALIDATE,
    EXECUTION__FAIL,
    EXECUTION__SKIPPED,
    EXECUTION__XFAIL,
    EXECUTION__XPASS,
    EXECUTION__HARD_ERROR,
    EXECUTION__IMPLEMENTATION_ERROR,
]
