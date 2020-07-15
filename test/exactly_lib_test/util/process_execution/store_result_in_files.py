import pathlib
import unittest

from exactly_lib.util import exception
from exactly_lib.util.process_execution import process_output_files, file_ctx_managers
from exactly_lib.util.process_execution.execution_elements import with_no_timeout
from exactly_lib.util.process_execution.executors import store_result_in_files as sut
from exactly_lib.util.process_execution.executors.store_result_in_files import ExitCodeAndFiles
from exactly_lib.util.process_execution.process_executor import ProcessExecutor, ProcessExecutionException
from exactly_lib.util.process_execution.process_output_files import FileNames
from exactly_lib_test.test_resources.files import tmp_dir
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe, py_programs
from exactly_lib_test.test_resources.value_assertions import file_assertions as fa
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.process_execution.test_resources import executables
from exactly_lib_test.util.test_resources.py_program import program_that_prints_and_exits_with_exit_code


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestExecutorThatStoresResultInFilesInDir)


class TestExecutorThatStoresResultInFilesInDir(unittest.TestCase):

    def test_exit_code(self):
        # ARRANGE #
        exit_code = 3

        program_file = File(
            'program.py',
            py_programs.py_pgm_with_stdout_stderr_exit_code(exit_code=exit_code),
        )
        with tmp_dir.tmp_dir(DirContents([
            program_file
        ])) as tmp_dir_path:
            executor = sut.ExecutorThatStoresResultInFilesInDir(ProcessExecutor(),
                                                                tmp_dir_path,
                                                                file_ctx_managers.dev_null(),
                                                                )
            # ACT #
            result = executor.execute(with_no_timeout(),
                                      py_exe.args_for_interpreting3(tmp_dir_path / program_file.name))
            # ASSERT #
            self.assertEqual(exit_code,
                             result.exit_code,
                             'Exit code')

    def test_stdin_SHOULD_be_passed_to_process(self):
        # ARRANGE #

        program_file = File(
            'stdin-2-stdout.py',
            py_programs.py_pgm_that_copies_stdin_to_stdout(),
        )
        stdin_file = File(
            'stdin.txt',
            'contents of stdin',
        )
        dir_contents = DirContents([
            program_file,
            stdin_file,
        ])
        with tmp_dir.tmp_dir_as_cwd(dir_contents):
            output_dir = pathlib.Path('output')
            executor = sut.ExecutorThatStoresResultInFilesInDir(
                ProcessExecutor(),
                output_dir,
                file_ctx_managers.open_file(stdin_file.name_as_path, 'r'),
            )
            # ACT #
            result = executor.execute(with_no_timeout(),
                                      py_exe.args_for_interpreting3(program_file.name))
            # ASSERT #
            assert_is_success_and_output_dir_contains_at_exactly_result_files(
                self,
                output_dir,
                SubProcessResult(
                    exitcode=0,
                    stdout=stdin_file.contents,
                    stderr='',
                ),
                result,
            )

    def test_invalid_executable_SHOULD_raise_process_execution_exception(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as tmp_dir_path:
            with self.assertRaises(ProcessExecutionException) as ctx:
                executor = sut.ExecutorThatStoresResultInFilesInDir(ProcessExecutor(),
                                                                    tmp_dir_path,
                                                                    file_ctx_managers.dev_null(),
                                                                    )
                # ACT & ASSERT #
                executor.execute(
                    with_no_timeout(),
                    executables.for_executable_file(tmp_dir_path / 'non-existing-program'),
                )
        assert isinstance(ctx.exception, ProcessExecutionException)
        self.assertIsInstance(ctx.exception.cause, Exception, 'exception info')

    def test_storage_of_result_in_files__existing_dir(self):
        # ARRANGE #
        py_pgm_file = File(
            'program.py',
            program_that_prints_and_exits_with_exit_code(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS),
        )
        with tmp_dir.tmp_dir(DirContents([py_pgm_file])) as pgm_dir_path:
            with tmp_dir.tmp_dir() as output_dir_path:
                executor = sut.ExecutorThatStoresResultInFilesInDir(ProcessExecutor(),
                                                                    output_dir_path,
                                                                    file_ctx_managers.dev_null(),
                                                                    )
                # ACT #
                result = executor.execute(with_no_timeout(),
                                          py_exe.args_for_interpreting3(pgm_dir_path / py_pgm_file.name)
                                          )
                # ASSERT #
                assert_is_success_and_output_dir_contains_at_exactly_result_files(
                    self,
                    output_dir_path,
                    PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                    result,
                )

    def test_storage_of_result_in_files__non_existing_dir(self):
        # ARRANGE #
        py_pgm_file = File(
            'program.py',
            program_that_prints_and_exits_with_exit_code(PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS),
        )
        with tmp_dir.tmp_dir(DirContents([py_pgm_file])) as pgm_dir_path:
            with tmp_dir.tmp_dir() as output_dir_path:
                non_existing_output_sub_dir_path = output_dir_path / 'non-existing'
                executor = sut.ExecutorThatStoresResultInFilesInDir(ProcessExecutor(),
                                                                    non_existing_output_sub_dir_path,
                                                                    file_ctx_managers.dev_null(),
                                                                    )
                # ACT #
                result = executor.execute(with_no_timeout(),
                                          py_exe.args_for_interpreting3(pgm_dir_path / py_pgm_file.name)
                                          )
                # ASSERT #
                assert_is_success_and_output_dir_contains_at_exactly_result_files(
                    self,
                    non_existing_output_sub_dir_path,
                    PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS,
                    result,
                )

    def test_fail_WHEN_storage_dir_is_an_existing_regular_file(self):
        # ARRANGE #
        successful_py_program = File(
            'successful.py',
            py_programs.py_pgm_with_stdout_stderr_exit_code(exit_code=0),
        )
        existing_file = File.empty('a-file')
        dir_contents = DirContents([successful_py_program, existing_file])

        with tmp_dir.tmp_dir(dir_contents) as tmp_dir_path:
            path_of_existing_regular_file = tmp_dir_path / existing_file.name
            executor = sut.ExecutorThatStoresResultInFilesInDir(
                ProcessExecutor(),
                path_of_existing_regular_file,
                file_ctx_managers.dev_null(),
            )
            with self.assertRaises(exception.ImplementationError) as ctx:
                # ACT & ASSERT #
                executor.execute(
                    with_no_timeout(),
                    executables.for_executable_file(tmp_dir_path / successful_py_program.name),
                )
        assert isinstance(ctx.exception, exception.ImplementationError)
        self.assertIsInstance(ctx.exception.message, str, 'exception info')


PROCESS_OUTPUT_WITH_NON_ZERO_EXIT_STATUS = SubProcessResult(exitcode=4,
                                                            stdout='on stdout',
                                                            stderr='on stderr')


def assert_is_success_and_output_dir_contains_at_exactly_result_files(put: unittest.TestCase,
                                                                      expected_storage_dir: pathlib.Path,
                                                                      expected: SubProcessResult,
                                                                      actual: ExitCodeAndFiles):
    put.assertEqual(expected.exitcode,
                    actual.exit_code,
                    'Exit code')
    put.assertEqual(expected_storage_dir,
                    actual.files.directory,
                    'storage dir')
    contents_assertion = assert_dir_contains_exactly_result_files(expected,
                                                                  actual.files.file_names)
    contents_assertion.apply(put, actual.files.directory)


def assert_dir_contains_exactly_result_files(expected: SubProcessResult,
                                             file_names: FileNames = process_output_files.FILE_NAMES
                                             ) -> ValueAssertion:
    return fa.dir_contains_exactly(DirContents([
        File(file_names.exit_code,
             str(expected.exitcode)),
        File(file_names.stdout,
             expected.stdout),
        File(file_names.stderr,
             expected.stderr),
    ]))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
