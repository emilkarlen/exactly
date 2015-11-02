from shellcheck_lib.test_case import error_description
from shellcheck_lib.test_case.test_case_processing import ErrorInfo


def of_message(message: str) -> ErrorInfo:
    return ErrorInfo(error_description.of_message(message))


def of_exception(exception: Exception) -> ErrorInfo:
    return ErrorInfo(error_description.of_exception(exception))
