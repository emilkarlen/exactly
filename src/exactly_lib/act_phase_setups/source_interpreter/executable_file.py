import pathlib

from exactly_lib.act_phase_setups.source_interpreter import parser_and_executor as pa
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceInterpreterSetup
from exactly_lib.act_phase_setups.util.command_resolvers import program_with_args
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.symbol.data import list_resolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case_utils.sub_proc.command_resolvers import CommandResolverForProgramAndArguments
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import CommandResolver


def new_for_script_language_setup(script_language_setup: SourceInterpreterSetup) -> ActPhaseSetup:
    return ActPhaseSetup(Constructor(script_language_setup))


class Constructor(parts.Constructor):
    def __init__(self, script_language_setup: SourceInterpreterSetup):
        super().__init__(pa.Parser(),
                         parts.UnconditionallySuccessfulValidator,
                         lambda os_process_executor, environment, source_code: ExecutorForSourceInterpreterSetup(
                             os_process_executor,
                             script_language_setup,
                             source_code))


class ActSourceFileNameGeneratorForSourceInterpreterSetup(pa.ActSourceFileNameGenerator):
    FILE_NAME_STEM = 'act-source'

    def __init__(self,
                 script_language_setup: SourceInterpreterSetup):
        self.script_language_setup = script_language_setup

    def base_name(self) -> str:
        return self.script_language_setup.base_name_from_stem(self.FILE_NAME_STEM)


class ExecutorForSourceInterpreterSetup(pa.ExecutorBase):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 script_language_setup: SourceInterpreterSetup,
                 source_info: pa.SourceInfo):
        super().__init__(os_process_executor,
                         ActSourceFileNameGeneratorForSourceInterpreterSetup(script_language_setup),
                         source_info)
        self.script_language_setup = script_language_setup

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandResolver:
        script_file_path = self._source_file_path(script_output_dir_path)
        pgm_and_args = self.script_language_setup.command_and_args_for_executing_script_file(str(script_file_path))
        return CommandResolverForProgramAndArguments(
            program_with_args(pgm_and_args),
            list_resolver.empty(),
        )
