import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import List, Callable, Mapping, ContextManager

from exactly_lib.impls.types.string_source.command_output import string_source as sut
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.program.test_resources import commands
from exactly_lib_test.type_val_prims.string_source.test_resources import source_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSuccessfulScenariosWithProgramFromDifferentChannels(),
        unittest.makeSuite(TestNonZeroExitCode),
        TestWhenProgramIsUnableToExecuteResultShouldBeHardError(),
    ])


class TestSuccessfulScenariosWithProgramFromDifferentChannels(unittest.TestCase):
    def runTest(self):
        text_printed_by_program = 'the text printed by the program'
        for proc_output_file in ProcOutputFile:
            python_source = py_programs.single_line_pgm_that_prints_to(proc_output_file,
                                                                       text_printed_by_program)

            with self.subTest(output_channel=proc_output_file):
                source_constructor = _SourceConstructorForPySourceProgramViaCmdLine(
                    python_source,
                    ModelMaker(
                        ignore_exit_code=False,
                        output_channel_to_capture=proc_output_file,
                    )
                )
                checker = source_checker.Checker(
                    self,
                    source_constructor,
                    source_checker.Expectation(
                        asrt.equals(text_printed_by_program),
                        may_depend_on_external_resources=asrt.equals(True),
                    ),
                )
                # ACT & ASSERT #
                checker.check_2_seq_w_file_first_and_last()


class TestWhenProgramIsUnableToExecuteResultShouldBeHardError(unittest.TestCase):
    def runTest(self):
        for proc_output_file in ProcOutputFile:
            for ignore_exit_code in [False, True]:
                with self.subTest(ignore_exit_code=ignore_exit_code,
                                  proc_output_file=proc_output_file):
                    # ACT & ASSERT #
                    source_constructor = _SourceConstructorForExeFile(
                        Path('/the/path/of/a/non-existing/program'),
                        ModelMaker(
                            ignore_exit_code=ignore_exit_code,
                            output_channel_to_capture=proc_output_file,
                        )
                    )
                    checker = source_checker.Checker(
                        self,
                        source_constructor,
                        source_checker.Expectation.hard_error(
                            may_depend_on_external_resources=asrt.equals(True),
                        ),
                    )
                    # ACT & ASSERT #
                    checker.check_2_seq_w_file_first_and_last()


class OutputFileCase:
    def __init__(self,
                 output_file: ProcOutputFile,
                 program_output: Mapping[ProcOutputFile, str],
                 ):
        self.output_file = output_file
        self.program_output = program_output


class TestNonZeroExitCode(unittest.TestCase):
    def test_result_SHOULD_be_failure_WHEN_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[1, 69],
            ignore_exit_code=False,
            expected_primitive=self._contents_access_raises_hard_error
        )

    def test_result_SHOULD_be_success_WHEN_any_zero_exit_code_and_exit_code_is_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[0, 1, 2, 69],
            ignore_exit_code=True,
            expected_primitive=self._contents_is_output_from_program,
        )

    def _check_exit_codes(self,
                          exit_code_cases: List[int],
                          ignore_exit_code: bool,
                          expected_primitive: Callable[[str], source_checker.Expectation],
                          ):
        # ARRANGE #

        program_output = {
            ProcOutputFile.STDOUT: 'output on stdout',
            ProcOutputFile.STDERR: 'output on stderr',
        }

        for exit_code in exit_code_cases:
            py_program = py_programs.py_pgm_with_stdout_stderr_exit_code(
                exit_code=exit_code,
                stdout_output=program_output[ProcOutputFile.STDOUT],
                stderr_output=program_output[ProcOutputFile.STDERR],
            )
            for output_file in ProcOutputFile:
                expected_program_output = program_output[output_file]
                with self.subTest(exit_code=exit_code,
                                  output_file=output_file):
                    source_constructor = _SourceConstructorForPySourceProgramViaCmdLine(
                        py_program,
                        ModelMaker(
                            ignore_exit_code=ignore_exit_code,
                            output_channel_to_capture=output_file,
                        )
                    )
                    checker = source_checker.Checker(
                        self,
                        source_constructor,
                        expected_primitive(expected_program_output),
                    )
                    # ACT & ASSERT #
                    checker.check_2_seq_w_file_first_and_last()

    @staticmethod
    def _contents_access_raises_hard_error(contents_on_output_channel: str) -> source_checker.Expectation:
        return source_checker.Expectation.hard_error(
            may_depend_on_external_resources=asrt.equals(True)
        )

    @staticmethod
    def _contents_is_output_from_program(contents_on_output_channel: str) -> source_checker.Expectation:
        return source_checker.Expectation(
            contents=asrt.equals(contents_on_output_channel),
            may_depend_on_external_resources=asrt.equals(True)
        )


class ModelMaker:
    def __init__(self,
                 ignore_exit_code: bool,
                 output_channel_to_capture: ProcOutputFile,
                 ):
        self.ignore_exit_code = ignore_exit_code
        self.output_channel_to_capture = output_channel_to_capture

    def model_from(self,
                   app_env: ApplicationEnvironment,
                   command: Command,
                   ) -> StringSource:
        return sut.string_source(
            'structure header',
            self.ignore_exit_code,
            self.output_channel_to_capture,
            command,
            app_env.process_execution_settings,
            app_env.os_services.command_executor,
            app_env.tmp_files_space,
        )


class _SourceConstructorForPySourceProgramViaCmdLine(source_checker.SourceConstructor):
    def __init__(self,
                 py_source: str,
                 model_maker: ModelMaker,
                 ):
        self.py_source = py_source
        self.model_maker = model_maker

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringSource]:
        yield self.model_maker.model_from(
            app_env,
            commands.command_that_runs_py_src_via_cmd_line(self.py_source),
        )


class _SourceConstructorForExeFile(source_checker.SourceConstructor):
    def __init__(self,
                 exe_file: Path,
                 model_maker: ModelMaker,
                 ):
        self.exe_file = exe_file
        self.model_maker = model_maker

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringSource]:
        yield self.model_maker.model_from(
            app_env,
            commands.command_that_runs_executable_file(self.exe_file),
        )
