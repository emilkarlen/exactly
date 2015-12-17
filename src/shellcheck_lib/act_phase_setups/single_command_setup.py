import pathlib
import re
import shlex

from shellcheck_lib.act_phase_setups import utils
from shellcheck_lib.default.execution_mode.test_case.test_case_parser import PlainSourceActPhaseParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.std import StdFiles
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup, ActPhaseSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptLanguage
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh


def act_phase_setup(command_path_is_relative_home: bool) -> ActPhaseSetup:
    vt = _RelativePathIsRelativeHome() if command_path_is_relative_home else _PlainStatement()
    return ActPhaseSetup(PlainSourceActPhaseParser(),
                         _script_source_builder,
                         _ActProgramExecutorForSingleCommand(vt))


def _script_source_builder() -> ScriptSourceBuilder:
    return ScriptSourceBuilder(_ScriptLanguage())


class _ScriptLanguage(ScriptLanguage):
    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        return []


class _StatementValidatorAndTransformer:
    def validate(self,
                 home_dir_abs_path: pathlib.Path,
                 statement: str) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def transform(self,
                  home_dir_abs_path: pathlib.Path,
                  statement: str):
        raise NotImplementedError()


class _ActProgramExecutorForSingleCommand(ActProgramExecutor):
    def __init__(self,
                 validator_and_transformer: _StatementValidatorAndTransformer):
        self.validator_and_transformer = validator_and_transformer

    def validate(self,
                 home_dir: pathlib.Path,
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        res = self.__mandatory_validate(source)
        if res.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            return res
        res = self.validator_and_transformer.validate(home_dir, source.source_lines[0])
        if res.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            return res
        return svh.new_svh_success()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        pass

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> int:
        command_string = self.validator_and_transformer.transform(home_dir,
                                                                  source_setup.script_builder.source_lines[0])
        cmd_and_args = shlex.split(command_string)
        return utils.execute_cmd_and_args(cmd_and_args,
                                          std_files)

    def __mandatory_validate(self,
                             source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        num_source_lines = len(source.source_lines)
        if num_source_lines != 1:
            msg = 'There must be a single source line. Found {} lines'.format(num_source_lines)
            return svh.new_svh_validation_error(msg)
        if source.source_lines[0].isspace():
            msg = 'Source statement is white space'
            return svh.new_svh_validation_error(msg)
        return svh.new_svh_success()


class _PlainStatement(_StatementValidatorAndTransformer):
    def validate(self,
                 home_dir_abs_path: pathlib.Path,
                 statement: str) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def transform(self,
                  home_dir_abs_path: pathlib.Path,
                  statement: str) -> str:
        return statement


class _RelativePathIsRelativeHome(_StatementValidatorAndTransformer):
    SPACE_RE = re.compile('\\s')

    def validate(self,
                 home_dir_abs_path: pathlib.Path,
                 statement: str) -> svh.SuccessOrValidationErrorOrHardError:
        (command_path, space_and_arguments) = self.__abs_command_name_and_space_and_arguments(home_dir_abs_path,
                                                                                              statement)
        if not command_path.is_file():
            return svh.new_svh_validation_error('Not an existing file: ' + str(command_path))
        return svh.new_svh_success()

    def transform(self,
                  home_dir_abs_path: pathlib.Path,
                  statement: str) -> str:
        (command_path, space_and_arguments) = self.__abs_command_name_and_space_and_arguments(home_dir_abs_path,
                                                                                              statement)
        return str(command_path) + ('' if space_and_arguments is None else space_and_arguments)

    def __abs_command_name_and_space_and_arguments(self,
                                                   home_dir_abs_path: pathlib.Path,
                                                   non_stripped_statement: str) -> (pathlib.Path, str):
        (command_path_name, space_and_arguments) = self.__split_statement(non_stripped_statement)
        command_path = home_dir_abs_path / pathlib.Path(command_path_name)
        return command_path, space_and_arguments

    def __split_statement(self, non_stripped_statement: str) -> (str, str):
        stripped_statement = non_stripped_statement.strip()
        match = self.SPACE_RE.search(stripped_statement)
        if match is None:
            return stripped_statement, None
        else:
            return stripped_statement[:match.start()], stripped_statement[match.start():]
