import pathlib
import unittest

from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_PREPROCESSOR
from shellcheck_lib_test.test_resources import quoting
from shellcheck_lib_test.test_resources.file_structure import File, DirContents
from shellcheck_lib_test.test_resources.main_program import main_program_check_base
from shellcheck_lib_test.test_resources.process import SubProcessResult, SubProcessResultInfo
from shellcheck_lib_test.test_resources.value_assertion import ValueAssertion


class SetupForTestCaseBase(main_program_check_base.SetupBase):
    def test_case(self) -> str:
        raise NotImplementedError()

    def expected_result(self) -> ValueAssertion:
        """
        :return: A ValueAssertion where the value argument is SubProcessResultInfo
        """
        raise NotImplementedError()

    def check(self,
              put: unittest.TestCase,
              root_path: pathlib.Path,
              actual_result: SubProcessResult):
        result_info = SubProcessResultInfo(self.file_argument_based_at(root_path),
                                           actual_result)
        self.expected_result().apply(put, result_info)

    def file_argument_base_name(self) -> str:
        return 'test-case.tc'

    def file_argument_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / self.file_argument_base_name()


class SetupWithoutPreprocessor(SetupForTestCaseBase, main_program_check_base.SetupWithoutPreprocessor):
    def first_arguments(self,
                        root_path: pathlib.Path) -> list:
        return []

    def file_structure(self,
                       root_path: pathlib.Path) -> DirContents:
        return DirContents([File(self.file_argument_base_name(),
                                 self.test_case())])


class SetupWithPreprocessor(SetupForTestCaseBase, main_program_check_base.SetupWithPreprocessor):
    def first_arguments(self,
                        root_path: pathlib.Path,
                        python_executable_file_name: str,
                        preprocessor_source_file_name: str) -> list:
        return [OPTION_FOR_PREPROCESSOR,
                '%s %s' % (quoting.file_name(python_executable_file_name),
                           quoting.file_name(preprocessor_source_file_name))
                ]

    def file_structure(self,
                       root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        return DirContents([File(self.file_argument_base_name(),
                                 self.test_case())])

    def preprocessor_source(self) -> str:
        raise NotImplementedError()
