from contextlib import contextmanager
import os
import pathlib
import tempfile
from time import strftime, localtime
import unittest
import sys

from shellcheck_lib.test_case.preprocessor import IdentityPreprocessor, PreprocessorViaExternalProgram
from shellcheck_lib_test.util.with_tmp_file import lines_content


class TestIdentityPreprocessor(unittest.TestCase):
    def test(self):
        processor = IdentityPreprocessor()
        path = pathlib.Path('test-case-file.txt')
        source = 'test case source'
        result = processor.apply(path, source)
        self.assertEqual(source,
                         result)


@contextmanager
def test_case_and_preprocessor_source(test_case_source: str,
                                      preprocessor_py_source: str):
    """
    A contextmanager that gives a pair of pathlib.Path:s of temporary files:
    (test-case-file-path, preprocessor-source-file).
   """
    prefix = strftime("shellcheck-test-", localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-test-case-") as test_case_dir:
        test_case_path = pathlib.Path(test_case_dir) / 'test-case-file.txt'
        with test_case_path.open('w') as f:
            f.write(test_case_source)
        with tempfile.TemporaryDirectory(prefix=prefix + "-proprocessor-") as preproc_dir:
            preprocessor_file_path = pathlib.Path(preproc_dir) / 'preprocessor.py'
            with preprocessor_file_path.open('w') as f:
                f.write(preprocessor_py_source)
            yield (test_case_path, preprocessor_file_path)


class TestPreprocessorViaExternalProgram(unittest.TestCase):
    def test_cwd__should_be__directory_containing_test_case_during_preprocessing_and_then_restored(self):
        test_case_source = 'CURRENT_WORKING_DIRECTORY'
        preprocessor_that_search_replace_current_working_directory = lines_content(
            [
                "import os",
                "print(os.getcwd())",
            ]
        )
        cwd_before = os.getcwd()
        with test_case_and_preprocessor_source(test_case_source,
                                               preprocessor_that_search_replace_current_working_directory) \
                as (test_case_path,
                    preprocessor_file_path):
            pre_proc = PreprocessorViaExternalProgram([sys.executable, str(preprocessor_file_path)])

            result = pre_proc.apply(test_case_path, test_case_source)

            cwd_after = os.getcwd()
            self.assertEqual(cwd_before,
                             cwd_after,
                             'Current Working Directory should be restored')

            test_case_dir = test_case_path.parent
            expected_test_case_contents = str(test_case_dir) + os.linesep
            self.assertEqual(expected_test_case_contents,
                             result,
                             """Test case source is expected to be the name of the directory
                             that contains the test case.""")


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIdentityPreprocessor))
    return ret_val


if __name__ == '__main__':
    unittest.main()
