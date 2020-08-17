import pathlib
import unittest
from abc import ABC, abstractmethod
from typing import List

import exactly_lib.cli.definitions.common_cli_options as opt
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.main_program import main_program_check_base
from exactly_lib_test.test_resources.main_program.main_program_runner_utils import ARGUMENTS_FOR_TEST_INTERPRETER
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SetupBase(ABC):
    @abstractmethod
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        pass

    @abstractmethod
    def expected_exit_code(self) -> int:
        pass

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
        expectation = self.stdout_expectation(root_path)
        actual = self._translate_actual_stdout_before_assertion(actual_result.stdout)
        expectation.apply_with_message(put, actual, 'stdout')

    @abstractmethod
    def stdout_expectation(self, root_path: pathlib.Path) -> ValueAssertion[str]:
        pass

    def _translate_actual_stdout_before_assertion(self, output_on_stdout: str) -> str:
        return output_on_stdout


class SetupWStdoutLinesCheckBase(SetupBase, ABC):
    def expected_stdout_lines(self, root_path: pathlib.Path) -> List[str]:
        return self.expected_stdout_run_lines(root_path) + self.expected_stdout_reporting_lines(root_path)

    @abstractmethod
    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        pass

    @abstractmethod
    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        pass

    def stdout_expectation(self, root_path: pathlib.Path) -> ValueAssertion[str]:
        expected_lines = self.expected_stdout_lines(root_path)
        expected_str = lines_content(expected_lines)
        return asrt.equals(expected_str)


class SetupWithPreprocessor(main_program_check_base.SetupWithPreprocessor,
                            SetupWStdoutLinesCheckBase):
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
                        preprocessor_source_file_name: str) -> List[str]:
        return [opt.SUITE_COMMAND]

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
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
                               SetupWStdoutLinesCheckBase):
    """
    Setup that executes a suite that does not use a preprocessor.
    """

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def first_arguments(self,
                        root_path: pathlib.Path) -> List[str]:
        return [opt.SUITE_COMMAND]

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
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


class SetupWithoutPreprocessorWithTestActor(SetupWithoutPreprocessor, ABC):
    """
    Setup that executes a suite that does not use a preprocessor,
    and uses the test actor as default for test cases.
    """

    def arguments_for_interpreter(self) -> List[str]:
        return ARGUMENTS_FOR_TEST_INTERPRETER


class SetupWithoutPreprocessorWithDefaultActor(SetupWithoutPreprocessor, ABC):
    """
    Setup that executes a suite that does not use a preprocessor.
    """

    def arguments_for_interpreter(self) -> List[str]:
        return []
