import pathlib
import unittest

from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_PREPROCESSOR
from shellcheck_lib_test.test_resources import quoting
from shellcheck_lib_test.test_resources.file_structure import File, DirContents
from shellcheck_lib_test.test_resources.main_program import main_program_check_base
from shellcheck_lib_test.test_resources.main_program.main_program_check_base import check_with_pre_proc
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResult, ExpectedSubProcessResult


class SetupWithPreprocessor(main_program_check_base.SetupWithPreprocessor):
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


class TestsForSetupWithPreprocessorBase(unittest.TestCase):
    def __init__(self, main_program_runner: MainProgramRunner):
        super().__init__()
        self.main_program_runner = main_program_runner

    def setup(self) -> SetupWithPreprocessor:
        raise NotImplementedError()

    def runTest(self):
        setup = self.setup()
        check_with_pre_proc([],
                            setup,
                            self,
                            self.main_program_runner)


class TestForSetupWithPreprocessor(unittest.TestCase):
    def __init__(self,
                 setup: SetupWithPreprocessor,
                 main_program_runner: MainProgramRunner):
        super().__init__()
        self.setup = setup
        self.main_program_runner = main_program_runner

    def runTest(self):
        check_with_pre_proc([],
                            self.setup,
                            self,
                            self.main_program_runner)
        # with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-preprocessor-') as pre_proc_dir:
        #     preprocessor_file_path = resolved_path(pre_proc_dir) / 'preprocessor.py'
        #     with preprocessor_file_path.open('w') as f:
        #         f.write(setup.preprocessor_source())
        #     with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-dir-contents-') as tmp_dir:
        #         tmp_dir_path = resolved_path(tmp_dir)
        #         file_structure = setup.file_structure(tmp_dir_path,
        #                                               sys.executable,
        #                                               str(preprocessor_file_path))
        #         file_structure.write_to(tmp_dir_path)
        #         file_argument = str(setup.file_argument_based_at(tmp_dir_path))
        #         first_arguments = setup.first_arguments(tmp_dir_path,
        #                                                 sys.executable,
        #                                                 str(preprocessor_file_path))
        #         arguments = first_arguments + ARGUMENTS_FOR_TEST_INTERPRETER + [file_argument]
        #         sub_process_result = self.main_program_runner.run(self, arguments)
        #         setup.check(self,
        #                     tmp_dir_path,
        #                     sub_process_result)

    def shortDescription(self):
        return str(type(self.setup)) + '/' + self.main_program_runner.description_for_test_name()


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
