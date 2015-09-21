from contextlib import contextmanager
import os
import pathlib
import unittest
import sys

from shellcheck_lib.test_case.preprocessor import IdentityPreprocessor, PreprocessorViaExternalProgram
from shellcheck_lib.test_case.test_case_processing import ProcessError
from shellcheck_lib_test.util.file_structure import DirContents, File
from shellcheck_lib_test.util.preprocessor_utils import dir_contents_and_preprocessor_source
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
    get_dir_contents = lambda x: DirContents([File('test-case-file.txt', test_case_source)])
    with dir_contents_and_preprocessor_source(get_dir_contents,
                                              preprocessor_py_source) as (dcr_path, pp_file_path):
        yield (dcr_path / 'test-case-file.txt', pp_file_path)


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

    def test_test_case_file_should_be_given_as_argument_to_preprocessor(self):
        test_case_source = '123'
        preprocessor_that_search_replace_current_working_directory = lines_content(
            [
                "import sys",
                "import os",
                "size=os.stat(sys.argv[1]).st_size",
                "sys.stdout.write(str(size))",
            ]
        )
        with test_case_and_preprocessor_source(test_case_source,
                                               preprocessor_that_search_replace_current_working_directory) \
                as (test_case_path,
                    preprocessor_file_path):
            pre_proc = PreprocessorViaExternalProgram([sys.executable, str(preprocessor_file_path)])

            result = pre_proc.apply(test_case_path, test_case_source)

            self.assertEqual('3',
                             result,
                             """Test case source is expected to be the size (in bytes) of the test case file.""")

    def test_exception_should_be_raised_when_test_case_file_does_not_exist(self):
        unused_test_case_source = ''
        preprocessor_that_opens_the_test_case_file = lines_content(
            [
                "import sys",
                "open(sys.argv[1])",
            ]
        )
        with test_case_and_preprocessor_source(unused_test_case_source,
                                               preprocessor_that_opens_the_test_case_file) \
                as (test_case_path,
                    preprocessor_file_path):
            pre_proc = PreprocessorViaExternalProgram([sys.executable, str(preprocessor_file_path)])

            with self.assertRaises(ProcessError) as ex_info:
                pre_proc.apply(pathlib.Path('non-existing-file-name'), unused_test_case_source)

    def test_exception_should_be_raised_when_preprocessor_does_not_exist(self):
        unused_test_case_source = ''
        preprocessor_that_opens_the_test_case_file = lines_content(
            [
                "import sys",
                "open(sys.argv[1])",
            ]
        )
        with test_case_and_preprocessor_source(unused_test_case_source,
                                               preprocessor_that_opens_the_test_case_file) \
                as (test_case_path,
                    preprocessor_file_path):
            pre_proc = PreprocessorViaExternalProgram(['non-existing-python-preprocessor',
                                                       str(preprocessor_file_path)])

            with self.assertRaises(ProcessError) as ex_info:
                pre_proc.apply(test_case_path, unused_test_case_source)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIdentityPreprocessor))
    return ret_val


if __name__ == '__main__':
    unittest.main()
