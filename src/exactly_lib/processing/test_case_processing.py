import pathlib
from enum import Enum

from exactly_lib.execution.result import FullResult
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.error_description import ErrorDescription
from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocationPath


class TestCaseSetup:
    def __init__(self,
                 file_path: pathlib.Path,
                 file_inclusion_relativity_root: pathlib.Path):
        self.__file_inclusion_relativity_root = file_inclusion_relativity_root
        self.__file_path = file_path

    @property
    def file_path(self) -> pathlib.Path:
        return self.__file_path

    @property
    def file_inclusion_relativity_root(self) -> pathlib.Path:
        return self.__file_inclusion_relativity_root


def test_case_setup_of_source_file(source_file: pathlib.Path) -> TestCaseSetup:
    return TestCaseSetup(source_file,
                         source_file.parent)


class ErrorInfo(tuple):
    def __new__(cls,
                description: ErrorDescription,
                source_location_path: line_source.SourceLocationPath = None,
                section_name: str = None):
        if description is not None:
            assert isinstance(description, ErrorDescription)
        return tuple.__new__(cls, (source_location_path, description, section_name))

    @property
    def source_location_path(self) -> line_source.SourceLocationPath:
        """
        :return: May be None
        """
        return self[0]

    @property
    def description(self) -> ErrorDescription:
        return self[1]

    @property
    def maybe_section_name(self) -> str:
        return self[2]


class Status(Enum):
    INTERNAL_ERROR = 1
    ACCESS_ERROR = 2
    EXECUTED = 3


class AccessErrorType(Enum):
    FILE_ACCESS_ERROR = 1
    PRE_PROCESS_ERROR = 2
    SYNTAX_ERROR = 3


class Result(tuple):
    def __new__(cls,
                status: Status,
                error_info: ErrorInfo = None,
                error_type: AccessErrorType = None,
                execution_result: FullResult = None):
        """
        :param error_info:
        :param error_type: Given iff status is Status.ACCESS_ERROR
        :param execution_result: Given iff status is Status.EXECUTED
        """
        return tuple.__new__(cls, (status, error_info, error_type, execution_result))

    @property
    def status(self) -> Status:
        return self[0]

    @property
    def error_info(self) -> ErrorInfo:
        return self[1]

    @property
    def access_error_type(self) -> AccessErrorType:
        return self[2]

    @property
    def execution_result(self) -> FullResult:
        return self[3]

    @property
    def source_location_path(self) -> SourceLocationPath:
        if self.error_info is not None:
            return self.error_info.source_location_path
        else:
            return self.execution_result.failure_info.source_location_path


def new_internal_error(error_info: ErrorInfo) -> Result:
    return Result(Status.INTERNAL_ERROR,
                  error_info=error_info)


def new_access_error(error: AccessErrorType,
                     error_info: ErrorInfo) -> Result:
    return Result(Status.ACCESS_ERROR,
                  error_info=error_info,
                  error_type=error)


def new_executed(execution_result: FullResult) -> Result:
    return Result(Status.EXECUTED,
                  execution_result=execution_result)


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
    def apply(self, test_case: TestCaseSetup) -> test_case_doc.TestCase:
        """
        :raises AccessorError
        """
        raise NotImplementedError()


class Processor:
    def apply(self, test_case: TestCaseSetup) -> Result:
        raise NotImplementedError()
