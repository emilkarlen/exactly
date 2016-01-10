import pathlib
import re

from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction
from shellcheck_lib.test_case.sections.act.phase_setup import PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.result import sh, svh


class ExecutableFileInstruction(ActPhaseInstruction):
    def __init__(self,
                 source: str):
        self.source_code = source
        self._vat = _RelativePathIsRelativeHome()

    def validate_pre_eds(self,
                         environment: common.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._vat.validate(environment.home_directory, self.source_code)

    def main(self, global_environment: common.GlobalEnvironmentForPostEdsPhase,
             script_generator: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        statement = self._vat.transform(global_environment.home_directory, self.source_code)
        script_generator.append.raw_script_statement(statement)
        return sh.new_sh_success()


class _StatementValidatorAndTransformer:
    def validate(self,
                 home_dir_abs_path: pathlib.Path,
                 statement: str) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def transform(self,
                  home_dir_abs_path: pathlib.Path,
                  statement: str):
        raise NotImplementedError()


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
        command_path = pathlib.Path(command_path_name)
        if not command_path.is_absolute():
            command_path = home_dir_abs_path / pathlib.Path(command_path_name)
        return command_path, space_and_arguments

    def __split_statement(self, non_stripped_statement: str) -> (str, str):
        stripped_statement = non_stripped_statement.strip()
        match = self.SPACE_RE.search(stripped_statement)
        if match is None:
            return stripped_statement, None
        else:
            return stripped_statement[:match.start()], stripped_statement[match.start():]
