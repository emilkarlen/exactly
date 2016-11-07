import unittest

from exactly_lib.instructions.utils import sub_process_execution as sut
from exactly_lib.instructions.utils.sub_process_execution import InstructionSourceInfo
from exactly_lib_test.act_phase_setups.test_resources.py_program import program_that_prints_and_exits_with_exit_code
from exactly_lib_test.test_resources import file_checks
from exactly_lib_test.test_resources import python_program_execution as py_exe
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.utils import sandbox_directory_structure
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class TestExecutorThatStoresResultInFilesInDir(unittest.TestCase):
    source_info = InstructionSourceInfo(4, 'instruction-name')

    def test_exit_code(self):
        exit_code = 3
        py_pgm_that_exits_with_exit_code = """
import sys
sys.exit(%d)
""" % exit_code

        with sandbox_directory_structure(contents=act_dir_contents(
                DirContents([
                    File('program.py', py_pgm_that_exits_with_exit_code)
                ]))) as sds:
            executor = sut.ExecutorThatStoresResultInFilesInDir(False)
            result = executor.apply(self.source_info,
                                    sds.log_dir,
                                    py_exe.args_for_interpreting(sds.act_dir / 'program.py'))
            self.assertTrue(result.is_success,
                            'Result should indicate success')
            self.assertEqual(exit_code,
                             result.exit_code,
                             'Exit code')

    def test_invalid_executable(self):
        with sandbox_directory_structure() as sds:
            executor = sut.ExecutorThatStoresResultInFilesInDir(False)
            result = executor.apply(self.source_info,
                                    sds.log_dir,
                                    [str(sds.act_dir / 'non-existing-program')])
            self.assertFalse(result.is_success,
                             'Result should indicate failure')

    def test_storage_of_result_in_files__existing_dir(self):
        with sandbox_directory_structure(contents=act_dir_contents(
                DirContents([
                    File('program.py',
                         program_that_prints_and_exits_with_exit_code(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS))
                ]))) as sds:
            executor = sut.ExecutorThatStoresResultInFilesInDir(False)
            result = executor.apply(self.source_info,
                                    sds.log_dir,
                                    py_exe.args_for_interpreting(sds.act_dir / 'program.py'))
            assert_is_success_and_output_dir_contains_at_least_result_files(self,
                                                                            PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                                                                            result)

    def test_storage_of_result_in_files__non_existing_dir(self):
        with sandbox_directory_structure(contents=act_dir_contents(
                DirContents([
                    File('program.py',
                         program_that_prints_and_exits_with_exit_code(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS))
                ]))) as sds:
            executor = sut.ExecutorThatStoresResultInFilesInDir(False)
            result = executor.apply(self.source_info,
                                    sds.log_dir / 'non-existing-path-component' / 'one-more-component',
                                    py_exe.args_for_interpreting(sds.act_dir / 'program.py'))
            assert_is_success_and_output_dir_contains_at_least_result_files(self,
                                                                            PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                                                                            result)


PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS = SubProcessResult(exitcode=4,
                                                            stdout='on stdout',
                                                            stderr='on stderr')


def assert_is_success_and_output_dir_contains_at_least_result_files(put: unittest.TestCase,
                                                                    expected: SubProcessResult,
                                                                    actual: sut.Result):
    put.assertTrue(actual.is_success,
                   'Result should indicate success')
    put.assertEqual(expected.exitcode,
                    actual.exit_code,
                    'Exit code')
    contents_assertion = assert_dir_contains_at_least_result_files(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                                                                   actual.file_names)
    contents_assertion.apply(put, actual.output_dir_path)


def assert_dir_contains_at_least_result_files(expected: SubProcessResult,
                                              file_names: sut.FileNames = sut.FILE_NAMES) -> va.ValueAssertion:
    return file_checks.dir_contains_at_least__va(DirContents([
        File(file_names.exit_code,
             str(expected.exitcode)),
        File(file_names.stdout,
             expected.stdout),
        File(file_names.stderr,
             expected.stderr),
    ]))


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestExecutorThatStoresResultInFilesInDir)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
