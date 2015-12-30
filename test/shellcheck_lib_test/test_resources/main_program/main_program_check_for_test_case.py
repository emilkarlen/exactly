import pathlib
import unittest

from shellcheck_lib_test.test_resources.file_structure import File, DirContents
from shellcheck_lib_test.test_resources.main_program import main_program_check_base
from shellcheck_lib_test.test_resources.process import SubProcessResult, ExpectedSubProcessResult


class SetupWithPreprocessor(main_program_check_base.SetupWithPreprocessor):
    def first_arguments(self,
                        root_path: pathlib.Path,
                        python_executable_file_name: str,
                        preprocessor_source_file_name: str) -> list:
        return ['--preprocessor',
                '%s %s' % (python_executable_file_name, preprocessor_source_file_name)
                ]

    def file_structure(self,
                       root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        return DirContents([File(self.file_argument_base_name(),
                                 self.test_case())])

    def file_argument_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / self.file_argument_base_name()

    def file_argument_base_name(self) -> str:
        return 'test-case.tc'

    def preprocessor_source(self) -> str:
        raise NotImplementedError()

    def test_case(self) -> str:
        raise NotImplementedError()

    def expected_result(self) -> ExpectedSubProcessResult:
        raise NotImplementedError()

    def check(self,
              put: unittest.TestCase,
              root_path: pathlib.Path,
              actual_result: SubProcessResult):
        self.expected_result().assert_matches(put, actual_result)


class TestsForSetupWithPreprocessorInternally(unittest.TestCase):
    def _check(self,
               additional_arguments: list,
               setup: SetupWithPreprocessor):
        main_program_check_base.check_with_pre_proc(additional_arguments, setup, self,
                                                    main_program_check_base.run_internally)


class TestsForSetupWithPreprocessorExternally(unittest.TestCase):
    def _check(self,
               additional_arguments: list,
               setup: SetupWithPreprocessor):
        main_program_check_base.check_with_pre_proc(additional_arguments, setup, self,
                                                    main_program_check_base.run_in_sub_process)
