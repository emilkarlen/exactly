import pathlib
import unittest
from typing import List

from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib_test.test_resources import string_formatting
from exactly_lib_test.test_resources.files.file_structure import File, DirContents, FileSystemElement
from exactly_lib_test.test_resources.main_program import main_program_check_base
from exactly_lib_test.test_resources.process import SubProcessResult, SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SetupForTestCaseBase(main_program_check_base.SetupBase):
    def test_case(self) -> str:
        raise NotImplementedError()

    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
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
                        root_path: pathlib.Path) -> List[str]:
        return []

    def file_structure(self,
                       root_path: pathlib.Path) -> DirContents:
        return DirContents([File(self.file_argument_base_name(),
                                 self.test_case())])


class SetupWithoutPreprocessorAndTestActor(SetupWithoutPreprocessor):
    def first_arguments(self,
                        root_path: pathlib.Path) -> List[str]:
        return []

    def file_structure(self,
                       root_path: pathlib.Path) -> DirContents:
        return DirContents([File(self.file_argument_base_name(),
                                 self.test_case())])


class SetupWithoutPreprocessorAndDefaultActor(SetupWithoutPreprocessor):
    def first_arguments(self, root_path: pathlib.Path) -> List[str]:
        return []

    def file_structure(self,
                       root_path: pathlib.Path) -> DirContents:
        test_case_file_list = [File(self.file_argument_base_name(), self.test_case())]
        return DirContents(test_case_file_list +
                           self._additional_files_in_file_structure(root_path))

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> List[FileSystemElement]:
        return []

    def arguments_for_interpreter(self) -> List[str]:
        return []


class SetupWithPreprocessorAndTestActor(SetupForTestCaseBase, main_program_check_base.SetupWithPreprocessor):
    def first_arguments(self,
                        root_path: pathlib.Path,
                        python_executable_file_name: str,
                        preprocessor_source_file_name: str) -> List[str]:
        return [OPTION_FOR_PREPROCESSOR,
                '%s %s' % (string_formatting.file_name(python_executable_file_name),
                           string_formatting.file_name(preprocessor_source_file_name))
                ]

    def file_structure(self,
                       root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        return DirContents([File(self.file_argument_base_name(),
                                 self.test_case())])

    def preprocessor_source(self) -> str:
        raise NotImplementedError()
