import tempfile
import unittest
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Sequence

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.types.string_source.command_output import string_source as sut
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorWithMaxNumInvocations
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources import application_environment
from exactly_lib_test.type_val_prims.program.test_resources import commands
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import SourceConstructorsBuilder
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces


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
                   command_stdin: Sequence[StringSource] = (),
                   ) -> StringSource:
        return sut.string_source(
            'structure header',
            self.ignore_exit_code,
            self.output_channel_to_capture,
            CommandWStdin(command, command_stdin),
            app_env.process_execution_settings,
            app_env.os_services.command_executor,
            self.mem_buff_size,
            app_env.tmp_files_space,
        )


class SourceConstructorsBuilderBase(SourceConstructorsBuilder, ABC):
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


class SourceConstructorForPySourceProgramViaCmdLine(SourceConstructorsBuilderBase):
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
