import pathlib
import unittest

import exactly_lib.cli.cli_environment.common_cli_options as opt
from exactly_lib_test.cli.test_resources.execute_main_program import ARGUMENTS_FOR_TEST_INTERPRETER
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.main_program import main_program_check_base
from exactly_lib_test.test_resources.process import SubProcessResult


class SetupBase:
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return self.expected_stdout_run_lines(root_path) + self.expected_stdout_reporting_lines(root_path)

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def _check_base(self,
                    put: unittest.TestCase,
                    root_path: pathlib.Path,
                    actual_result: SubProcessResult):
        self._check_exitcode(put, actual_result)
        self._check_stdout(put, root_path, actual_result)

    def _check_exitcode(self,
                        put: unittest.TestCase,
                        actual_result: SubProcessResult):
        put.assertEqual(self.expected_exit_code(),
                        actual_result.exitcode,
                        'Exit Code\n' + actual_result.stderr)

    def _check_stdout(self,
                      put: unittest.TestCase,
                      root_path: pathlib.Path,
                      actual_result: SubProcessResult):
        expected_lines = self.expected_stdout_lines(root_path)
        if expected_lines is not None:
            actual_lines = self._translate_actual_stdout_before_assertion(actual_result.stdout).splitlines()
            line_number = 0
            for expected_line, actual_line in zip(expected_lines, actual_lines):
                if isinstance(expected_line, str):
                    put.assertEqual(expected_line, actual_line,
                                    'Output of line ' + str(line_number))
                else:
                    match = expected_line.fullmatch(actual_line)
                    if match is None:
                        put.fail('Expecting match of "%s" (actual: "%s")' % (str(expected_line), actual_line))
            put.assertEqual(len(expected_lines),
                            len(actual_lines),
                            'Expecting ' + str(len(expected_lines)) + ' lines')

    def _translate_actual_stdout_before_assertion(self, output_on_stdout: str) -> str:
        return output_on_stdout


class SetupWithPreprocessor(main_program_check_base.SetupWithPreprocessor,
                            SetupBase):
    """
    Setup that executes a suite that may use a preprocessor
    written in python.
    """

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def first_arguments(self,
                        root_path: pathlib.Path,
                        python_executable_file_name: str,
                        preprocessor_source_file_name: str) -> list:
        return [opt.SUITE_COMMAND]

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def file_argument_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return self.root_suite_file_based_at(root_path)

    def check(self,
              put: unittest.TestCase,
              root_path: pathlib.Path,
              actual_result: SubProcessResult):
        self._check_base(put, root_path, actual_result)

    def preprocessor_source(self) -> str:
        raise NotImplementedError()

    def file_structure(self,
                       root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        raise NotImplementedError()


class SetupWithoutPreprocessor(main_program_check_base.SetupWithoutPreprocessor,
                               SetupBase):
    """
    Setup that executes a suite that does not use a preprocessor.
    """

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def first_arguments(self,
                        root_path: pathlib.Path) -> list:
        return [opt.SUITE_COMMAND]

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def file_argument_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return self.root_suite_file_based_at(root_path)

    def check(self,
              put: unittest.TestCase,
              root_path: pathlib.Path,
              actual_result: SubProcessResult):
        self._check_base(put, root_path, actual_result)

    def file_structure(self,
                       root_path: pathlib.Path) -> DirContents:
        raise NotImplementedError()


class SetupWithoutPreprocessorWithTestActor(SetupWithoutPreprocessor):
    """
    Setup that executes a suite that does not use a preprocessor,
    and uses the test actor as default for test cases.
    """

    def arguments_for_interpreter(self) -> list:
        return ARGUMENTS_FOR_TEST_INTERPRETER


class SetupWithoutPreprocessorWithDefaultActor(SetupWithoutPreprocessor):
    """
    Setup that executes a suite that does not use a preprocessor.
    """

    def arguments_for_interpreter(self) -> list:
        return []
