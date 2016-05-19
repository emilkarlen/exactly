from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_case import error_description


def of_message(message: str) -> ErrorInfo:
    return ErrorInfo(error_description.of_message(message))


def of_exception(exception: Exception) -> ErrorInfo:
    return ErrorInfo(error_description.of_exception(exception))
