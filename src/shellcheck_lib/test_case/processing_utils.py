import pathlib

from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case import test_case_processing as processing


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


class ProcessError(Exception):
    def __init__(self, error_info: ErrorInfo):
        self._error_info = error_info

    @property
    def error_info(self) -> ErrorInfo:
        return self._error_info


class SourceReader:
    def apply(self, test_case_file_path: pathlib.Path) -> str:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class Preprocessor:
    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class Parser:
    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class Executor:
    def apply(self,
              test_case: processing.TestCase) -> FullResult:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class AccessorError(Exception):
    def __init__(self,
                 error: processing.AccessErrorType,
                 error_info: ErrorInfo):
        self._error = error
        self._error_info = error_info

    @property
    def error(self) -> processing.AccessErrorType:
        return self._error

    @property
    def error_info(self) -> ErrorInfo:
        return self._error_info


class IdentityPreprocessor(Preprocessor):
    """
    A pre-processor that does nothing.
    """

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return test_case_source


class Accessor:
    def __init__(self,
                 source_reader: SourceReader,
                 pre_processor: Preprocessor,
                 parser: Parser):
        self._source_reader = source_reader
        self._pre_processor = pre_processor
        self._parser = parser

    def apply(self,
              test_case_file_path: pathlib.Path) -> test_case_doc.TestCase:
        """
        :raises AccessorError
        """
        source = self._apply(self._source_reader.apply,
                             processing.AccessErrorType.FILE_ACCESS_ERROR,
                             test_case_file_path)
        preprocessed_source = self._apply(self._pre_processor.apply,
                                          processing.AccessErrorType.PRE_PROCESS_ERROR,
                                          test_case_file_path,
                                          source)
        return self._apply(self._parser.apply,
                           processing.AccessErrorType.PARSE_ERROR,
                           test_case_file_path,
                           preprocessed_source
                           )

    @staticmethod
    def _apply(f, error_type: processing.AccessErrorType, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ProcessError as ex:
            raise AccessorError(error_type,
                                ex.error_info)


class ProcessorFromAccessorAndExecutor(processing.Processor):
    def __init__(self,
                 accessor: Accessor,
                 executor: Executor):
        self._accessor = accessor
        self._executor = executor

    def apply(self, test_case: processing.TestCase) -> processing.Result:
        try:
            a_test_case_doc = self._accessor.apply(test_case.file_path)
        except AccessorError as ex:
            return processing.Result(processing.Status.ACCESS_ERROR,
                                     message=ex.error_info.message,
                                     error_type=ex.error)
        full_result = self._executor.apply(a_test_case_doc)
        return processing.Result(processing.Status.EXECUTED,
                                 full_result=full_result)
