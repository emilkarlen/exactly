import pathlib
import unittest

from exactly_lib.document.model import new_empty_phase_contents
from exactly_lib.execution.result import FullResult, new_skipped
from exactly_lib.test_case import error_description
from exactly_lib.test_case import processing_utils as sut
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case import test_case_processing as tcp
from exactly_lib.test_case.preprocessor import IdentityPreprocessor
from shellcheck_lib_test.test_case.test_resources import error_info


class TestIdentityPreprocessor(unittest.TestCase):
    def test(self):
        # ACT #
        actual = IdentityPreprocessor().apply(PATH, 'source')
        # ASSERT #
        self.assertEqual('source',
                         actual)


class TestAccessor(unittest.TestCase):
    def test_source_reader_that_raises(self):
        # ARRANGE #
        accessor = sut.AccessorFromParts(SourceReaderThat(raises(PROCESS_ERROR)),
                                         PreprocessorThat(raises_should_not_be_invoked_error),
                                         ParserThat(raises_should_not_be_invoked_error))
        # ACT #
        with self.assertRaises(tcp.AccessorError) as cm:
            accessor.apply(PATH)
        # ASSERT #
        self.assertEqual(cm.exception.error,
                         tcp.AccessErrorType.FILE_ACCESS_ERROR)

    def test_preprocessor_that_raises(self):
        # ARRANGE #
        accessor = sut.AccessorFromParts(SourceReaderThat(gives_constant('source')),
                                         PreprocessorThat(raises(PROCESS_ERROR)),
                                         ParserThat(raises_should_not_be_invoked_error))
        # ACT #
        with self.assertRaises(tcp.AccessorError) as cm:
            accessor.apply(PATH)
        # ASSERT #
        self.assertEqual(cm.exception.error,
                         tcp.AccessErrorType.PRE_PROCESS_ERROR)

    def test_parser_that_raises(self):
        # ARRANGE #
        accessor = sut.AccessorFromParts(SourceReaderThat(gives_constant('source')),
                                         PreprocessorThat(gives_constant('preprocessed source')),
                                         ParserThat(raises(PROCESS_ERROR)))
        # ACT #
        with self.assertRaises(tcp.AccessorError) as cm:
            accessor.apply(PATH)
        # ASSERT #
        self.assertEqual(cm.exception.error,
                         tcp.AccessErrorType.PARSE_ERROR)

    def test_successful_application(self):
        # ARRANGE #
        source = 'SOURCE'
        p_source = 'PREPROCESSED SOURCE'
        accessor = sut.AccessorFromParts(SourceReaderThatReturnsIfSame(PATH, source),
                                         PreprocessorThatReturnsIfSame(source, p_source),
                                         ParserThatReturnsIfSame(p_source, TEST_CASE))
        # ACT #
        actual = accessor.apply(PATH)
        # ASSERT #
        self.assertIs(TEST_CASE,
                      actual)


class TestProcessorFromAccessorAndExecutor(unittest.TestCase):
    def test_accessor_exception_from_accessor(self):
        # ARRANGE #
        process_error = tcp.ProcessError(
            error_info.of_exception(ValueError('exception message')))
        accessor = sut.AccessorFromParts(SourceReaderThat(raises(process_error)),
                                         PreprocessorThat(gives_constant('preprocessed source')),
                                         ParserThat(gives_constant(TEST_CASE)))
        executor = ExecutorThat(raises(PROCESS_ERROR))
        processor = sut.ProcessorFromAccessorAndExecutor(accessor,
                                                         executor)
        # ACT #
        result = processor.apply(tcp.TestCaseSetup(PATH))
        # ASSERT #
        self.assertIs(tcp.Status.ACCESS_ERROR,
                      result.status)
        self.assertIs(tcp.AccessErrorType.FILE_ACCESS_ERROR,
                      result.access_error_type)
        self.assertIsNotNone(result.error_info,
                             'There should be ErrorInfo')
        err_description = result.error_info.description
        self.assertIsInstance(err_description,
                              error_description.ErrorDescriptionOfException)
        assert isinstance(err_description,
                          error_description.ErrorDescriptionOfException)
        self.assertEqual(err_description.exception.args[0],
                         'exception message')

    def test_implementation_exception_from_accessor(self):
        # ARRANGE #
        accessor = sut.AccessorFromParts(SourceReaderThat(raises(RuntimeError())),
                                         PreprocessorThat(gives_constant('preprocessed source')),
                                         ParserThat(gives_constant(TEST_CASE)))
        executor = ExecutorThat(raises(PROCESS_ERROR))
        processor = sut.ProcessorFromAccessorAndExecutor(accessor,
                                                         executor)
        # ACT #
        result = processor.apply(tcp.TestCaseSetup(PATH))
        # ASSERT #
        self.assertEqual(tcp.Status.INTERNAL_ERROR,
                         result.status)

    def test_implementation_exception_from_executor(self):
        # ARRANGE #
        accessor = sut.AccessorFromParts(SourceReaderThat(gives_constant('source')),
                                         PreprocessorThat(gives_constant('preprocessed source')),
                                         ParserThat(gives_constant(TEST_CASE)))
        executor = ExecutorThat(raises(RuntimeError()))
        processor = sut.ProcessorFromAccessorAndExecutor(accessor,
                                                         executor)
        # ACT #
        result = processor.apply(tcp.TestCaseSetup(PATH))
        # ASSERT #
        self.assertEqual(tcp.Status.INTERNAL_ERROR,
                         result.status)

    def test_successful_application(self):
        # ARRANGE #
        accessor = sut.AccessorFromParts(SourceReaderThat(gives_constant('source')),
                                         PreprocessorThat(gives_constant('preprocessed source')),
                                         ParserThat(gives_constant(TEST_CASE)))
        full_result = new_skipped()
        executor = ExecutorThatReturnsIfSame(TEST_CASE, full_result)
        processor = sut.ProcessorFromAccessorAndExecutor(accessor,
                                                         executor)
        # ACT #
        result = processor.apply(tcp.TestCaseSetup(PATH))
        # ASSERT #
        self.assertIs(tcp.Status.EXECUTED,
                      result.status)
        self.assertIs(full_result,
                      result.execution_result)


class SourceReaderThat(sut.SourceReader):
    def __init__(self, f):
        self.f = f

    def apply(self, test_case_file_path: pathlib.Path) -> str:
        return self.f()


class SourceReaderThatReturnsIfSame(sut.SourceReader):
    def __init__(self, expected, returns):
        self.expected = expected
        self.returns = returns

    def apply(self, test_case_file_path: pathlib.Path) -> str:
        return if_same_then_else_raise(self.expected,
                                       test_case_file_path,
                                       self.returns)


class PreprocessorThat(tcp.Preprocessor):
    def __init__(self, f):
        self.f = f

    def apply(self, test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return self.f()


class PreprocessorThatReturnsIfSame(tcp.Preprocessor):
    def __init__(self, expected, returns):
        self.expected = expected
        self.returns = returns

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return if_same_then_else_raise(self.expected,
                                       test_case_source,
                                       self.returns)


class ParserThat(sut.Parser):
    def __init__(self, f):
        self.f = f

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        return self.f()


class ParserThatReturnsIfSame(sut.Parser):
    def __init__(self, expected, returns):
        self.expected = expected
        self.returns = returns

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        return if_same_then_else_raise(self.expected,
                                       test_case_plain_source,
                                       self.returns)


class ExecutorThat(sut.Executor):
    def __init__(self, f):
        self.f = f

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullResult:
        self.f()


class ExecutorThatReturnsIfSame(sut.Executor):
    def __init__(self, expected, returns):
        self.expected = expected
        self.returns = returns

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullResult:
        return if_same_then_else_raise(self.expected,
                                       test_case,
                                       self.returns)


def raises(e: Exception):
    def f():
        raise e

    return f


def gives_constant(x):
    return lambda: x


def raises_should_not_be_invoked_error():
    raise RuntimeError('should not be invoked')


def append_single_char_to_string(s: str) -> str:
    return s + 'x'


def if_same_then_else_raise(expected, actual, result):
    if actual is expected:
        return result
    else:
        raise RuntimeError('should not be invoked')


PROCESS_ERROR = tcp.ProcessError(tcp.ErrorInfo(error_description.of_exception(ValueError('exception message'))))

PATH = pathlib.Path('path')

TEST_CASE = test_case_doc.TestCase(new_empty_phase_contents(),
                                   new_empty_phase_contents(),
                                   new_empty_phase_contents(),
                                   new_empty_phase_contents(),
                                   new_empty_phase_contents(),
                                   new_empty_phase_contents())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIdentityPreprocessor))
    ret_val.addTest(unittest.makeSuite(TestAccessor))
    ret_val.addTest(unittest.makeSuite(TestProcessorFromAccessorAndExecutor))
    return ret_val


if __name__ == '__main__':
    unittest.main()
