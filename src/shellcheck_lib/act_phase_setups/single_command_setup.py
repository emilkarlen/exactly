import pathlib
import shlex

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.output import StdOutputFiles, StdFiles
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.act_phase_setups import utils
from shellcheck_lib.test_case.sections.act.script_source import ScriptLanguage


def script_language() -> ScriptLanguage:
    return _ScriptLanguage()


def act_program_executor() -> ActProgramExecutor:
    return _ActProgramExecutorForSingleCommand()


class _ScriptLanguage(ScriptLanguage):
    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        return []


# def new_for_script_language_setup(script_language_setup: ScriptLanguageSetup) -> ActPhaseSetup:
#     return ActPhaseSetup(PlainSourceActPhaseParser(),
#                          script_language_setup.new_builder,
#                          ActProgramExecutorForSingleCommand(script_language_setup))


class _ActProgramExecutorForSingleCommand(ActProgramExecutor):
    def validate(self,
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        num_source_lines = len(source.source_lines)
        if num_source_lines == 1:
            return svh.new_svh_success()
        msg = 'There must be a single source line. Found {} lines'.format(num_source_lines)
        return svh.new_svh_validation_error(msg)

    def prepare(self,
                source_setup: SourceSetup,
                eds: ExecutionDirectoryStructure):
        pass

    def execute(self,
                source_setup: SourceSetup,
                cwd_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                stdin,
                std_output_files: StdOutputFiles) -> int:
        command_string = source_setup.script_builder.build()
        cmd_and_args = shlex.split(command_string)
        return utils.execute_cmd_and_args(cmd_and_args,
                                          cwd_dir_path,
                                          StdFiles(stdin_file=stdin,
                                                   output_files=std_output_files))
