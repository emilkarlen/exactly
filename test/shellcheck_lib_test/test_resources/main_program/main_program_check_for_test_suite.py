import pathlib
import unittest

from shellcheck_lib_test.test_resources.file_structure import DirContents
from shellcheck_lib_test.test_resources.main_program import main_program_check_base
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResult


class SetupBase:
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def suite_begin(self, file_path: pathlib.Path) -> str:
        return 'SUITE ' + str(file_path) + ': BEGIN'

    def suite_end(self, file_path: pathlib.Path) -> str:
        return 'SUITE ' + str(file_path) + ': END'

    def case(self, file_path: pathlib.Path, status: str) -> str:
        return 'CASE  ' + str(file_path) + ': ' + status

    def additional_arguments(self) -> list:
        """
        Arguments that appears before the suite file argument.
        :return:
        """
        return []

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
                        'Exit Code')

    def _check_stdout(self,
                      put: unittest.TestCase,
                      root_path: pathlib.Path,
                      actual_result: SubProcessResult):
        expected_lines = self.expected_stdout_lines(root_path)
        if expected_lines is not None:
            actual_lines = actual_result.stdout.splitlines()
            put.assertEqual(expected_lines,
                            actual_lines,
                            'Output on stdout')


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
        return ['suite']

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
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
        return ['suite']

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
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


# class SetupWithoutPreprocessor(SetupBase):
#     def file_structure(self, root_path: pathlib.Path) -> DirContents:
#         raise NotImplementedError()


class TestsForSetupWithPreprocessorInternally(unittest.TestCase):
    def _check(self, setup: SetupWithPreprocessor):
        main_program_check_base.check_with_pre_proc(setup.additional_arguments(), setup, self,
                                                    main_program_check_base.run_internally)


class TestsForSetupWithPreprocessorExternally(unittest.TestCase):
    def _check(self, setup: SetupWithPreprocessor):
        main_program_check_base.check_with_pre_proc(setup.additional_arguments(), setup, self,
                                                    main_program_check_base.run_in_sub_process)


class TestsForSetupWithoutPreprocessorInternally(unittest.TestCase):
    def _check(self, setup: SetupWithoutPreprocessor):
        main_program_check_base.check(setup.additional_arguments(), setup, self,
                                      main_program_check_base.run_internally)


class TestsForSetupWithoutPreprocessorExternally(unittest.TestCase):
    def _check(self, setup: SetupWithoutPreprocessor):
        main_program_check_base.check(setup.additional_arguments(), setup, self,
                                      main_program_check_base.run_in_sub_process)


class TestForSetupWithoutPreprocessor(unittest.TestCase):
    def __init__(self,
                 setup: SetupWithoutPreprocessor,
                 main_program_runner: MainProgramRunner):
        super().__init__()
        self.setup = setup
        self.main_program_runner = main_program_runner

    def runTest(self):
        main_program_check_base.check(self.setup.additional_arguments(),
                                      self.setup, self,
                                      self.main_program_runner)

    def shortDescription(self):
        return str(type(self.setup)) + '/' + self.main_program_runner.description_for_test_name()


class TestForSetupWithPreprocessor(unittest.TestCase):
    def __init__(self,
                 setup: SetupWithPreprocessor,
                 main_program_runner: MainProgramRunner):
        super().__init__()
        self.setup = setup
        self.main_program_runner = main_program_runner

    def runTest(self):
        main_program_check_base.check_with_pre_proc(self.setup.additional_arguments(),
                                                    self.setup, self,
                                                    self.main_program_runner)

    def shortDescription(self):
        return str(type(self.setup)) + '/' + self.main_program_runner.description_for_test_name()
