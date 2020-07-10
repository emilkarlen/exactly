import unittest

import exactly_lib.util.process_execution.result
from exactly_lib.util.process_execution import process_output_files, sub_process_execution as sut
from exactly_lib.util.process_execution.execution_elements import with_no_timeout
from exactly_lib.util.process_execution.process_output_files import FileNames
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import file_assertions as fa
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.process_execution.test_resources import executables
from exactly_lib_test.util.test_resources.py_program import program_that_prints_and_exits_with_exit_code


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestExecutorThatStoresResultInFilesInDir)


class TestExecutorThatStoresResultInFilesInDir(unittest.TestCase):

    def test_exit_code(self):
        exit_code = 3
        py_pgm_that_exits_with_exit_code = """
import sys
sys.exit(%d)
""" % exit_code

        with tmp_dir(DirContents([
            File('logic_symbol_utils.py', py_pgm_that_exits_with_exit_code)
        ])) as tmp_dir_path:
            executor = sut.ExecutorThatStoresResultInFilesInDir(with_no_timeout())
            result = executor.execute(tmp_dir_path,
                                      py_exe.args_for_interpreting3(tmp_dir_path / 'logic_symbol_utils.py'))
            self.assertTrue(result.is_success,
                            'Result should indicate success')
            self.assertEqual(exit_code,
                             result.exit_code,
                             'Exit code')

    def test_invalid_executable(self):
        with tmp_dir() as tmp_dir_path:
            executor = sut.ExecutorThatStoresResultInFilesInDir(with_no_timeout())
            result = executor.execute(tmp_dir_path,
                                      executables.for_executable_file(tmp_dir_path / 'non-existing-program')
                                      )
            self.assertFalse(result.is_success,
                             'Result should indicate failure')

    def test_storage_of_result_in_files__existing_dir(self):
        with tmp_dir(DirContents([
            File('logic_symbol_utils.py',
                 program_that_prints_and_exits_with_exit_code(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS))
        ])) as tmp_dir_path:
            executor = sut.ExecutorThatStoresResultInFilesInDir(with_no_timeout())
            result = executor.execute(tmp_dir_path,
                                      py_exe.args_for_interpreting3(tmp_dir_path / 'logic_symbol_utils.py')
                                      )
            assert_is_success_and_output_dir_contains_at_least_result_files(self,
                                                                            PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                                                                            result)

    def test_storage_of_result_in_files__non_existing_dir(self):
        with tmp_dir(DirContents([
            File('logic_symbol_utils.py',
                 program_that_prints_and_exits_with_exit_code(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS))
        ])) as tmp_dir_path:
            executor = sut.ExecutorThatStoresResultInFilesInDir(with_no_timeout())
            result = executor.execute(tmp_dir_path / 'non-existing-path-component' / 'one-more-component',
                                      py_exe.args_for_interpreting3(tmp_dir_path / 'logic_symbol_utils.py'))
            assert_is_success_and_output_dir_contains_at_least_result_files(self,
                                                                            PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                                                                            result)


PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS = SubProcessResult(exitcode=4,
                                                            stdout='on stdout',
                                                            stderr='on stderr')


def assert_is_success_and_output_dir_contains_at_least_result_files(put: unittest.TestCase,
                                                                    expected: SubProcessResult,
                                                                    actual: exactly_lib.util.process_execution.result.Result):
    put.assertTrue(actual.is_success,
                   'Result should indicate success')
    put.assertEqual(expected.exitcode,
                    actual.exit_code,
                    'Exit code')
    contents_assertion = assert_dir_contains_at_least_result_files(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                                                                   actual.file_names)
    contents_assertion.apply(put, actual.output_dir_path)


def assert_dir_contains_at_least_result_files(expected: SubProcessResult,
                                              file_names: FileNames = process_output_files.FILE_NAMES
                                              ) -> ValueAssertion:
    return fa.dir_contains_at_least(DirContents([
        File(file_names.exit_code,
             str(expected.exitcode)),
        File(file_names.stdout,
             expected.stdout),
        File(file_names.stderr,
             expected.stderr),
    ]))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
