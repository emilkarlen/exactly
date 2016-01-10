import unittest

from shellcheck_lib.instructions.utils import sub_process_execution as sut
from shellcheck_lib.instructions.utils.sub_process_execution import InstructionSourceInfo, InstructionMetaInfo
from shellcheck_lib_test.test_resources import file_checks
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.execution.eds_populator import act_dir_contents
from shellcheck_lib_test.test_resources.execution.utils import execution_directory_structure
from shellcheck_lib_test.test_resources.file_structure import DirContents, File


class TestExecutorThatLogsResultUnderPhaseDir(unittest.TestCase):
    source_info = InstructionSourceInfo(InstructionMetaInfo('phase-name',
                                                            'instruction-name'),
                                        4)

    def test_exit_code(self):
        exit_code = 3
        py_pgm_that_exits_with_exit_code = """
import sys
sys.exit(%d)
""" % exit_code

        with execution_directory_structure(contents=act_dir_contents(
                DirContents([
                    File('program.py', py_pgm_that_exits_with_exit_code)
                ]))) as eds:
            executor = sut.ExecutorThatLogsResultUnderPhaseDir()
            result = executor.apply(self.source_info,
                                    eds,
                                    py_exe.args_for_interpreting(eds.act_dir / 'program.py'))
            self.assertTrue(result.is_success,
                            'Result should indicate success')
            self.assertEqual(exit_code,
                             result.exit_code,
                             'Exit code')

    def test_invalid_executable(self):
        with execution_directory_structure() as eds:
            executor = sut.ExecutorThatLogsResultUnderPhaseDir()
            result = executor.apply(self.source_info,
                                    eds,
                                    [str(eds.act_dir / 'non-existing-program')])
            self.assertFalse(result.is_success,
                             'Result should indicate failure')

    def test_storage_of_result_in_files(self):
        stdout_contents = 'on stdout'
        stderr_contents = 'on stderr'
        exit_code = 4
        py_pgm_that_prints_and_exits_with_exit_code = """
import sys
sys.stdout.write('%s')
sys.stderr.write('%s')
sys.exit(%d)
""" % (stdout_contents, stderr_contents, exit_code)

        with execution_directory_structure(contents=act_dir_contents(
                DirContents([
                    File('program.py', py_pgm_that_prints_and_exits_with_exit_code)
                ]))) as eds:
            executor = sut.ExecutorThatLogsResultUnderPhaseDir()
            result = executor.apply(self.source_info,
                                    eds,
                                    py_exe.args_for_interpreting(eds.act_dir / 'program.py'))
            self.assertTrue(result.is_success,
                            'Result should indicate success')
            self.assertEqual(exit_code,
                             result.exit_code,
                             'Exit code')
            contents_assertion = file_checks.DirContainsAtLeast(DirContents([
                File(result.exit_code_file_name,
                     str(exit_code)),
                File(result.stdout_file_name,
                     stdout_contents),
                File(result.stderr_file_name,
                     stderr_contents),
            ]))
            contents_assertion.apply(self, result.output_dir_path)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestExecutorThatLogsResultUnderPhaseDir))
    return ret_val


if __name__ == '__main__':
    unittest.main()
