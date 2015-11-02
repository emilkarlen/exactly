import pathlib

from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.test_case import error_description
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case import test_case_processing as processing
from shellcheck_lib.test_case.test_case_processing import AccessorError, Accessor, ProcessError, Preprocessor, ErrorInfo


class SourceReader:
    def apply(self, test_case_file_path: pathlib.Path) -> str:
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
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullResult:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class AccessorFromParts(Accessor):
    def __init__(self,
                 source_reader: SourceReader,
                 pre_processor: Preprocessor,
                 parser: Parser):
        self._source_reader = source_reader
        self._pre_processor = pre_processor
        self._parser = parser

    def apply(self,
              test_case_file_path: pathlib.Path) -> test_case_doc.TestCase:
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
                 accessor: processing.Accessor,
                 executor: Executor):
        self._accessor = accessor
        self._executor = executor

    def apply(self, test_case: processing.TestCaseSetup) -> processing.Result:
        try:
            try:
                a_test_case_doc = self._accessor.apply(test_case.file_path)
            except AccessorError as ex:
                return processing.Result(processing.Status.ACCESS_ERROR,
                                         error_info=ex.error_info,
                                         error_type=ex.error)
            full_result = self._executor.apply(test_case.file_path,
                                               a_test_case_doc)
            return processing.new_executed(full_result)
        except Exception as ex:
            return processing.new_internal_error(ErrorInfo(error_description.of_exception(ex)))
