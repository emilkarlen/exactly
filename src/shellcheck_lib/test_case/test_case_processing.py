from enum import Enum
import pathlib

from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.execution.result import FullResult


class TestCaseSetup:
    def __init__(self,
                 file_path: pathlib.Path):
        self.__file_path = file_path

    @property
    def file_path(self) -> pathlib.Path:
        return self.__file_path


class Status(Enum):
    INTERNAL_ERROR = 1
    ACCESS_ERROR = 2
    EXECUTED = 3


class AccessErrorType(Enum):
    FILE_ACCESS_ERROR = 1
    PRE_PROCESS_ERROR = 2
    PARSE_ERROR = 3


class Result(tuple):
    def __new__(cls,
                status: Status,
                message: str=None,
                error_type: AccessErrorType=None,
                execution_result: FullResult=None):
        """
        Exactly only one of the arguments must be non-None.
        """
        return tuple.__new__(cls, (status, message, error_type, execution_result))

    @property
    def status(self) -> Status:
        return self[0]

    @property
    def message(self) -> str:
        return self[1]

    @property
    def error_type(self) -> AccessErrorType:
        return self[2]

    @property
    def execution_result(self) -> FullResult:
        return self[3]


def new_internal_error(message: str) -> Result:
    return Result(Status.INTERNAL_ERROR,
                  message=message)


def new_access_error(error: AccessErrorType) -> Result:
    return Result(Status.ACCESS_ERROR,
                  error_type=error)


def new_executed(execution_result: FullResult) -> Result:
    return Result(Status.EXECUTED,
                  execution_result=execution_result)


class ErrorInfo(tuple):
    def __new__(cls,
                message: str=None,
                file_path: pathlib.Path=None,
                line: line_source.Line=None,
                exception: Exception=None):
        return tuple.__new__(cls, (message, file_path, line, exception))

    @property
    def message(self) -> str:
        return self[0]

    @property
    def file(self) -> pathlib.Path:
        return self[1]

    @property
    def line(self) -> line_source.Line:
        return self[2]

    @property
    def exception(self) -> Exception:
        return self[3]


class AccessorError(Exception):
    def __init__(self,
                 error: AccessErrorType,
                 error_info: ErrorInfo):
        self._error = error
        self._error_info = error_info

    @property
    def error(self) -> AccessErrorType:
        return self._error

    @property
    def error_info(self) -> ErrorInfo:
        return self._error_info


class ProcessError(Exception):
    def __init__(self, error_info: ErrorInfo):
        self._error_info = error_info

    @property
    def error_info(self) -> ErrorInfo:
        return self._error_info


class Preprocessor:
    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class Accessor:
    def apply(self,
              test_case_file_path: pathlib.Path) -> test_case_doc.TestCase:
        """
        :raises AccessorError
        """
        raise NotImplementedError()


class Processor:
    def apply(self, test_case: TestCaseSetup) -> Result:
        raise NotImplementedError()
