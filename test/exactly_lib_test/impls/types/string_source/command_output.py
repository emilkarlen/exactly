import tempfile
import unittest
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import List, Callable, Mapping, ContextManager

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.types.string_source.command_output import string_source as sut
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorWithMaxNumInvocations
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources import application_environment
from exactly_lib_test.type_val_prims.program.test_resources import commands
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import SourceConstructorsBuilder
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSuccessfulScenariosWithProgramFromDifferentChannels(),
        unittest.makeSuite(TestNonZeroExitCode),
        TestWhenProgramIsUnableToExecuteResultShouldBeHardError(),
    ])


class TestSuccessfulScenariosWithProgramFromDifferentChannels(unittest.TestCase):
    def runTest(self):
        text_printed_by_program = 'the text printed by the program'
        mem_buff_size_cases = [
            NameAndValue(
                'output fits in mem buff',
                len(text_printed_by_program),
            ),
            NameAndValue(
                'output do not fit in mem buff',
                len(text_printed_by_program) - 1,
            ),
        ]
        for proc_output_file in ProcOutputFile:
            python_source = py_programs.single_line_pgm_that_prints_to(proc_output_file,
                                                                       text_printed_by_program)
            for mem_buff_size_case in mem_buff_size_cases:
                frozen_may_depend_on_external_resources = len(text_printed_by_program) > mem_buff_size_case.value
                with self.subTest(output_channel=proc_output_file,
                                  mem_buff_size_case=mem_buff_size_case.name):
                    source_constructors = _SourceConstructorForPySourceProgramViaCmdLine(
                        python_source,
                        ModelMaker(
                            ignore_exit_code=False,
                            output_channel_to_capture=proc_output_file,
                            mem_buff_size=mem_buff_size_case.value,
                        )
                    )
                    assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(
                        multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                            text_printed_by_program,
                            may_depend_on_external_resources=asrt.equals(True),
                            frozen_may_depend_on_external_resources=asrt.equals(
                                frozen_may_depend_on_external_resources),
                        ),
                    )
                    # ACT & ASSERT #
                    assertion.apply_without_message(
                        self,
                        source_constructors.build(),
                    )


class TestWhenProgramIsUnableToExecuteResultShouldBeHardError(unittest.TestCase):
    def runTest(self):
        for proc_output_file in ProcOutputFile:
            for ignore_exit_code in [False, True]:
                with self.subTest(ignore_exit_code=ignore_exit_code,
                                  proc_output_file=proc_output_file):
                    # ACT & ASSERT #
                    source_constructor = _SourceConstructorsForExeFile(
                        Path('/the/path/of/a/non-existing/program'),
                        ModelMaker(
                            ignore_exit_code=ignore_exit_code,
                            output_channel_to_capture=proc_output_file,
                            mem_buff_size=2 ** 10
                        )
                    )
                    assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(
                        multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.hard_error(
                            may_depend_on_external_resources=asrt_string_source.ext_dependencies_gives(True),
                        ),
                    )
                    # ACT & ASSERT #
                    assertion.apply_without_message(
                        self,
                        source_constructor.build(),
                    )


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
                          expected_primitive: Callable[[str], multi_obj_assertions.ExpectationOnUnFrozenAndFrozen],
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
                    source_constructors = _SourceConstructorForPySourceProgramViaCmdLine(
                        py_program,
                        ModelMaker(
                            ignore_exit_code=ignore_exit_code,
                            output_channel_to_capture=output_file,
                            mem_buff_size=1,
                        )
                    )
                    assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(
                        expected_primitive(expected_program_output),
                    )
                    # ACT & ASSERT #
                    assertion.apply_without_message(
                        self,
                        source_constructors.build(),
                    )

    @staticmethod
    def _contents_access_raises_hard_error(contents_on_output_channel: str,
                                           ) -> multi_obj_assertions.ExpectationOnUnFrozenAndFrozen:
        return multi_obj_assertions.ExpectationOnUnFrozenAndFrozen(
            multi_obj_assertions.Expectation.hard_error(
                may_depend_on_external_resources=asrt_string_source.ext_dependencies_gives(True),
            ),
            frozen_may_depend_on_external_resources=asrt_string_source.ext_dependencies_raises_hard_error()
        )

    @staticmethod
    def _contents_is_output_from_program(contents_on_output_channel: str,
                                         ) -> multi_obj_assertions.ExpectationOnUnFrozenAndFrozen:
        return multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            contents_on_output_channel,
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.equals(True),
        )


class ModelMaker:
    def __init__(self,
                 ignore_exit_code: bool,
                 output_channel_to_capture: ProcOutputFile,
                 mem_buff_size: int,
                 ):
        self.ignore_exit_code = ignore_exit_code
        self.output_channel_to_capture = output_channel_to_capture
        self.mem_buff_size = mem_buff_size

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
            self.mem_buff_size,
            app_env.tmp_files_space,
        )


class _SourceConstructorsBuilderBase(SourceConstructorsBuilder, ABC):
    @contextmanager
    def dir_file_space_with_existing_dir(self) -> ContextManager[DirFileSpace]:
        with tempfile.TemporaryDirectory(prefix='exactly') as tmp_dir_name:
            yield tmp_file_spaces.tmp_dir_file_space_for_test(Path(tmp_dir_name))

    def app_env_for_no_freeze(self,
                              put: unittest.TestCase,
                              message_builder: MessageBuilder,
                              ) -> ContextManager[ApplicationEnvironment]:
        return application_environment.application_environment_with_existing_dir()

    def app_env_for_freeze(self,
                           put: unittest.TestCase,
                           message_builder: MessageBuilder,
                           ) -> ContextManager[ApplicationEnvironment]:
        default_os_services = os_services_access.new_for_current_os()
        os_services_w_check = os_services_access.new_for_cmd_exe(
            CommandExecutorWithMaxNumInvocations(
                put,
                1,
                default_os_services.command_executor,
                message_builder.apply(''),
            )
        )
        return application_environment.application_environment_with_existing_dir(os_services_w_check)


class _SourceConstructorForPySourceProgramViaCmdLine(_SourceConstructorsBuilderBase):
    def __init__(self,
                 py_source: str,
                 model_maker: ModelMaker,
                 ):
        super().__init__()
        self.py_source = py_source
        self.model_maker = model_maker

    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment) -> StringSource:
        return self.model_maker.model_from(
            app_env,
            commands.command_that_runs_py_src_via_cmd_line(self.py_source),
        )


class _SourceConstructorsForExeFile(_SourceConstructorsBuilderBase):
    def __init__(self,
                 exe_file: Path,
                 model_maker: ModelMaker,
                 ):
        super().__init__()
        self.exe_file = exe_file
        self.model_maker = model_maker

    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment) -> StringSource:
        return self.model_maker.model_from(
            app_env,
            commands.command_that_runs_executable_file(self.exe_file),
        )
