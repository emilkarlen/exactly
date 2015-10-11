import pathlib
import subprocess

from shellcheck_lib.default.execution_mode.test_case.test_case_parser import PlainSourceActPhaseParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general import exception
from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.script_language.script_language_management import ScriptLanguageSetup
from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup, ActScriptExecutor, SourceSetup
from shellcheck_lib.test_case.sections.result import svh


def new_for_script_language_setup(script_language_setup: ScriptLanguageSetup) -> ActPhaseSetup:
    return ActPhaseSetup(PlainSourceActPhaseParser(),
                         script_language_setup.new_builder,
                         ActScriptExecutorForScriptLanguage(script_language_setup))


class ActScriptExecutorForScriptLanguage(ActScriptExecutor):
    def __init__(self,
                 script_language_setup: ScriptLanguageSetup):
        self.script_language_setup = script_language_setup

    def validate(self,
                 source_setup: SourceSetup) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def prepare(self,
                source_setup: SourceSetup,
                eds: ExecutionDirectoryStructure):
        script_file_path = self._script_path(source_setup)
        with open(str(script_file_path), 'w') as f:
            f.write(source_setup.script_builder.build())

    def execute(self,
                source_setup: SourceSetup,
                cwd_dir_path: pathlib.Path,
                esd: ExecutionDirectoryStructure,
                stdin,
                std_files: StdOutputFiles) -> int:
        script_file_path = self._script_path(source_setup)
        cmd_and_args = self.script_language_setup.command_and_args_for_executing_script_file(
            str(script_file_path))
        try:
            return subprocess.call(cmd_and_args,
                                   cwd=str(cwd_dir_path),
                                   stdin=stdin,
                                   stdout=std_files.out,
                                   stderr=std_files.err)
        except ValueError as ex:
            msg = 'Error executing act phase as subprocess: ' + str(ex)
            raise exception.ImplementationError(msg)
        except OSError as ex:
            msg = 'Error executing act phase as subprocess: ' + str(ex)
            raise exception.ImplementationError(msg)

    def _script_path(self,
                     source_setup: SourceSetup) -> pathlib.Path:
        base_name = self.script_language_setup.base_name_from_stem(source_setup.script_file_stem)
        return source_setup.script_output_dir_path / base_name
