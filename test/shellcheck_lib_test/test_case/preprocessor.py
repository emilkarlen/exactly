import os
import pathlib
import tempfile
from time import strftime, localtime
import unittest

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


class TestPreprocessorViaExternalProgram(unittest.TestCase):
    def test_cwd__should_be__directory_containing_test_case_during_preprocessing_and_then_restored(self):
        test_case_source = 'CURRENT_WORKING_DIRECTORY'
        preprocessor_that_search_replace_current_working_directory = lines_content(
            [
                "import os",
                "import sys",

                "cwd = os.getcwd()",
                "f = open(sys.argv[1])",
                "for line in f:",
                "    print(line.replace('CURRENT_WORKING_DIRECTORY', cwd))",
                "f.close()"
            ]
        )
        cwd_before = os.getcwd()
        try:
            prefix = strftime("shellcheck-test-", localtime())
            with tempfile.TemporaryDirectory(prefix=prefix + "-test-case-") as test_case_dir:
                test_case_path = pathlib.Path(test_case_dir) / 'test-case-file.txt'
                with test_case_path.open('w') as f:
                    f.write(test_case_source)
                with tempfile.TemporaryDirectory(prefix=prefix + "-proprocessor-") as preproc_dir:
                    preprocessor_file_path = pathlib.Path(preproc_dir) / 'preprocessor.py'
                    with preprocessor_file_path.open('w') as f:
                        f.write(preprocessor_that_search_replace_current_working_directory)

                    pre_proc = PreprocessorViaExternalProgram(['python3', str(preprocessor_file_path)])

                    result = pre_proc.apply(test_case_path, test_case_source)

                    cwd_after = os.getcwd()
                    self.assertEqual(cwd_before,
                                     cwd_after,
                                     'Current Working Directory should be restored')

                    expected_test_case_contents = test_case_dir + os.linesep
                    self.assertEqual(expected_test_case_contents, result)
        finally:
            os.chdir(cwd_before)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIdentityPreprocessor))
    return ret_val


if __name__ == '__main__':
    unittest.main()
