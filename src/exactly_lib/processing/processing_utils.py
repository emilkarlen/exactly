import pathlib

from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.processing import test_case_processing as processing
from exactly_lib.processing.test_case_handling_setup import TestCaseTransformer
from exactly_lib.processing.test_case_processing import AccessorError, Accessor, ProcessError, Preprocessor, ErrorInfo, \
    TestCaseFileReference
from exactly_lib.test_case import error_description
from exactly_lib.test_case import test_case_doc


class SourceReader:
    def apply(self, test_case_file_path: pathlib.Path) -> str:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class Parser:
    def apply(self,
              test_case: TestCaseFileReference,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        """
        :raises ProcessError: Indicates syntax error
        :raises AccessorError: An error with explicit error type
        """
        raise NotImplementedError()


class Executor:
    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullExeResult:
        """
        :raises ProcessError:
        """
        raise NotImplementedError()


class AccessorFromParts(Accessor):
    def __init__(self,
                 source_reader: SourceReader,
                 pre_processor: Preprocessor,
                 parser: Parser,
                 transformer: TestCaseTransformer):
        self._source_reader = source_reader
        self._pre_processor = pre_processor
        self._parser = parser
        self._transformer = transformer

    def apply(self, test_case: TestCaseFileReference) -> test_case_doc.TestCase:
        source = self._apply(self._source_reader.apply,
                             processing.AccessErrorType.FILE_ACCESS_ERROR,
                             test_case.file_path)
        preprocessed_source = self._apply(self._pre_processor.apply,
                                          processing.AccessErrorType.PRE_PROCESS_ERROR,
                                          test_case.file_path,
                                          source)
        test_case = self._apply(self._parser.apply,
                                processing.AccessErrorType.SYNTAX_ERROR,
                                test_case,
                                preprocessed_source
                                )
        return self._transformer.transform(test_case)

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

    def apply(self, test_case: processing.TestCaseFileReference) -> processing.Result:
        try:
            try:
                a_test_case_doc = self._accessor.apply(test_case)
            except AccessorError as ex:
                return processing.Result(processing.Status.ACCESS_ERROR,
                                         error_info=ex.error_info,
                                         error_type=ex.error)
            full_result = self._executor.apply(test_case.file_path,
                                               a_test_case_doc)
            return processing.new_executed(full_result)
        except Exception as ex:
            return processing.new_internal_error(ErrorInfo(error_description.of_exception(ex)))
