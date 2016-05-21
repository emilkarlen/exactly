import pathlib

from exactly_lib.act_phase_setups import utils
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguageSetup
from exactly_lib.act_phase_setups.source_parser_and_instruction import PlainSourceActPhaseParser
from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor, ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


def new_for_script_language_setup(script_language_setup: ScriptLanguageSetup) -> ActPhaseSetup:
    return ActPhaseSetup(PlainSourceActPhaseParser(),
                         script_language_setup.new_builder,
                         ActSourceExecutorForScriptLanguage(script_language_setup))


class ActSourceExecutorForScriptLanguage(ActSourceExecutor):
    def __init__(self,
                 script_language_setup: ScriptLanguageSetup):
        self.script_language_setup = script_language_setup

    def validate(self,
                 source: ActSourceBuilder,
                 home_dir: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        script_file_path = self._script_path(source_setup)
        with open(str(script_file_path), 'w') as f:
            f.write(source_setup.script_builder.build())

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        script_file_path = self._script_path(source_setup)
        cmd_and_args = self.script_language_setup.command_and_args_for_executing_script_file(
            str(script_file_path))
        exit_code = utils.execute_cmd_and_args(cmd_and_args,
                                               std_files)
        return new_eh_exit_code(exit_code)

    def _script_path(self,
                     source_setup: SourceSetup) -> pathlib.Path:
        base_name = self.script_language_setup.base_name_from_stem(source_setup.script_file_stem)
        return source_setup.script_output_dir_path / base_name
