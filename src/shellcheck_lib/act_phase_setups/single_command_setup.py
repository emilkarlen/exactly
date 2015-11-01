import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.test_case_parser import PlainSourceActPhaseParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.output import StdOutputFiles, StdFiles
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup, ActPhaseSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.act_phase_setups import utils
from shellcheck_lib.test_case.sections.act.script_source import ScriptLanguage


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(PlainSourceActPhaseParser(),
                         _script_source_builder,
                         _ActProgramExecutorForSingleCommand())


def _script_source_builder() -> ScriptSourceBuilder:
    return ScriptSourceBuilder(_ScriptLanguage())


class _ScriptLanguage(ScriptLanguage):
    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        return []


class _ActProgramExecutorForSingleCommand(ActProgramExecutor):
    def validate(self,
                 home_dir: pathlib.Path,
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        num_source_lines = len(source.source_lines)
        if num_source_lines != 1:
            msg = 'There must be a single source line. Found {} lines'.format(num_source_lines)
            return svh.new_svh_validation_error(msg)
        if source.source_lines[0].isspace():
            msg = 'Source statement is white space'
            return svh.new_svh_validation_error(msg)
        return svh.new_svh_success()

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
        command_string = source_setup.script_builder.source_lines[0]
        cmd_and_args = shlex.split(command_string)
        return utils.execute_cmd_and_args(cmd_and_args,
                                          cwd_dir_path,
                                          StdFiles(stdin_file=stdin,
                                                   output_files=std_output_files))
