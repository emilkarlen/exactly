import pathlib

from exactly_lib.actors.source_interpreter import parser_and_executor as pa
from exactly_lib.actors.source_interpreter.source_file_management import SourceInterpreterSetup
from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import AtcOsProcessExecutor, Actor
from exactly_lib.test_case_utils.program.command import command_sdvs


def actor(setup: SourceInterpreterSetup) -> Actor:
    return Parser(setup)


class Parser(parts.ActorFromParts):
    def __init__(self, setup: SourceInterpreterSetup):
        super().__init__(pa.Parser(),
                         parts.UnconditionallySuccessfulValidator,
                         lambda os_process_executor, environment, source_code: ExecutorForSourceInterpreterSetup(
                             os_process_executor,
                             setup,
                             source_code))


class ActSourceFileNameGeneratorForSourceInterpreterSetup(pa.ActSourceFileNameGenerator):
    FILE_NAME_STEM = 'act-source'

    def __init__(self,
                 setup: SourceInterpreterSetup):
        self.setup = setup

    def base_name(self) -> str:
        return self.setup.base_name_from_stem(self.FILE_NAME_STEM)


class ExecutorForSourceInterpreterSetup(pa.ExecutorBase):
    def __init__(self,
                 os_process_executor: AtcOsProcessExecutor,
                 script_language_setup: SourceInterpreterSetup,
                 source_info: pa.SourceInfo):
        super().__init__(os_process_executor,
                         ActSourceFileNameGeneratorForSourceInterpreterSetup(script_language_setup),
                         source_info)
        self.script_language_setup = script_language_setup

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandSdv:
        script_file_path = self._source_file_path(script_output_dir_path)
        pgm_and_args = self.script_language_setup.command_and_args_for_executing_script_file(str(script_file_path))
        return command_sdvs.for_system_program__from_pgm_and_args(pgm_and_args)
