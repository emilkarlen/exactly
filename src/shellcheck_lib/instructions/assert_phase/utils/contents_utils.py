import filecmp
import pathlib

from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.file_utils import ensure_parent_directory_does_exist
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.instructions.assert_phase.utils import instruction_utils
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.os_services import OsServices

WITH_REPLACED_ENV_VARS_OPTION = '--with-replaced-env-vars'
SOURCE_REL_HOME_OPTION = '--rel-home'
SOURCE_REL_CWD_OPTION = '--rel-cwd'
EMPTY_ARGUMENT = 'empty'


class ComparisonSource:
    def __init__(self,
                 check_during_validation: bool,
                 file_name: str):
        self.check_during_validation = check_during_validation
        self.file_name = file_name

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


class ComparisonSourceForFileRelHome(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return global_environment.home_directory / self.file_name


class ComparisonSourceForFileRelCwd(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return pathlib.Path(self.file_name)


class ComparisonTarget:
    def __init__(self, do_check_file_properties: bool):
        self.do_check_file_properties = do_check_file_properties

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


class ActComparisonTarget(ComparisonTarget):
    def __init__(self,
                 file_name: str):
        super().__init__(True)
        self.file_name = file_name

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return pathlib.Path(self.file_name)


class StdoutComparisonTarget(ComparisonTarget):
    def __init__(self):
        super().__init__(False)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return global_environment.eds.result.stdout_file


class StderrComparisonTarget(ComparisonTarget):
    def __init__(self):
        super().__init__(False)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return global_environment.eds.result.stderr_file


def check(file_path: pathlib.Path) -> str:
    if not file_path.exists():
        return 'File does not exist: ' + str(file_path)
    if not file_path.is_file():
        return 'Not a regular file: ' + str(file_path)
    return None


class Checker:
    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class CheckerWithFileRelHome(Checker):
    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def comparison_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        target_file_name = str(self.target_file_path(eds))
        comparison_file_name = str(self.comparison_file_path(eds))
        if not filecmp.cmp(target_file_name, comparison_file_name, shallow=False):
            return pfh.new_pfh_fail('Unexpected content in file: ' + target_file_name)


class CheckerForComparisonWithFile(Checker):
    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def comparison_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        target_file_name = str(self.target_file_path(eds))
        comparison_file_name = str(self.comparison_file_path(eds))
        if not filecmp.cmp(target_file_name, comparison_file_name, shallow=False):
            return pfh.new_pfh_fail('Unexpected content in file: ' + target_file_name)


class CheckerForEmptiness(Checker):
    def __init__(self, expect_empty: bool):
        self._expect_empty = expect_empty

    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def comparison_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        size = self.target_file_path(eds).stat().st_size
        if self._expect_empty:
            if size != 0:
                return pfh.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        else:
            if size == 0:
                return pfh.new_pfh_fail('File is empty')
        return pfh.new_pfh_pass()


class ContentCheckerInstructionBase(AssertPhaseInstruction):
    def __init__(self,
                 comparison_source: ComparisonSource,
                 comparison_target: ComparisonTarget):
        self.comparison_target = comparison_target
        self._comparison_source = comparison_source

    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        if self._comparison_source.check_during_validation:
            error_message = check(self._comparison_source.file_path(global_environment))
            if error_message:
                return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        comparison_source_file_path = self._comparison_source.file_path(environment)
        error_message = check(comparison_source_file_path)
        if error_message:
            return pfh.new_pfh_fail(error_message)

        comparison_target_path = self.comparison_target.file_path(environment)
        if self.comparison_target.do_check_file_properties:
            error_message = check(comparison_target_path)
            if error_message:
                return pfh.new_pfh_fail(error_message)

        display_target_file_name = str(comparison_target_path)
        comparison_source_file_name = str(comparison_source_file_path)
        comparison_target_file_path = self._get_comparison_target_file_path(comparison_target_path,
                                                                            environment,
                                                                            os_services)
        comparison_target_file_name = str(comparison_target_file_path)
        if not filecmp.cmp(comparison_target_file_name, comparison_source_file_name, shallow=False):
            return pfh.new_pfh_fail('Unexpected content in file: ' + display_target_file_name)
        return pfh.new_pfh_pass()

    def _get_comparison_target_file_path(self,
                                         target_file_path: pathlib.Path,
                                         environment: i.GlobalEnvironmentForPostEdsPhase,
                                         os_services: OsServices) -> str:
        raise NotImplementedError()


class ContentCheckerInstruction(ContentCheckerInstructionBase):
    def __init__(self,
                 comparison_source: ComparisonSource,
                 comparison_target: ComparisonTarget):
        super().__init__(comparison_source, comparison_target)

    def _get_comparison_target_file_path(self,
                                         target_file_path: pathlib.Path,
                                         environment: i.GlobalEnvironmentForPostEdsPhase,
                                         os_services: OsServices) -> pathlib.Path:
        return target_file_path


class TargetTransformer:
    def replace_env_vars(self,
                         environment: GlobalEnvironmentForPostEdsPhase,
                         os_services: OsServices,
                         target_file_path: pathlib.Path) -> pathlib.Path:
        src_file_path = self._get_src_file_path(environment)
        dst_file_path = self._dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        env_vars_to_replace = environment_variables.all_environment_variables(environment.home_directory,
                                                                              environment.eds)
        self._replace_env_vars_and_write_result_to_dst(env_vars_to_replace,
                                                       src_file_path,
                                                       dst_file_path)
        return dst_file_path

    def _get_src_file_path(self, environment: GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()

    def _dst_file_path(self,
                       environment: GlobalEnvironmentForPostEdsPhase,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        """
        :return: An absolute path that does/should store the transformed version of
        the src file.
        """
        raise NotImplementedError()

    @staticmethod
    def _replace_env_vars_and_write_result_to_dst(env_vars_to_replace: dict,
                                                  src_file_path: pathlib.Path,
                                                  dst_file_path: pathlib.Path):
        with src_file_path.open() as src_file:
            # TODO Handle reading/replacing in chunks, if file is too large to be read in one chunk
            contents = src_file.read()
        for var_name, var_value in env_vars_to_replace.items():
            contents = contents.replace(var_value, var_name)
        ensure_parent_directory_does_exist(dst_file_path)
        with open(str(dst_file_path), 'w') as dst_file:
            dst_file.write(contents)


class ContentCheckerWithTransformationInstruction(ContentCheckerInstructionBase):
    def __init__(self,
                 comparison_source: ComparisonSource,
                 comparison_target: ComparisonTarget,
                 target_transformer: TargetTransformer):
        super().__init__(comparison_source, comparison_target)
        self.target_transformer = target_transformer

    def _get_comparison_target_file_path(self,
                                         target_file_path: pathlib.Path,
                                         environment: i.GlobalEnvironmentForPostEdsPhase,
                                         os_services: OsServices) -> pathlib.Path:
        return self.target_transformer.replace_env_vars(environment,
                                                        os_services,
                                                        target_file_path)


class EmptinessCheckerInstruction(instruction_utils.InstructionWithoutValidationBase):
    def __init__(self,
                 expect_empty: bool,
                 comparison_target: ComparisonTarget):
        self.comparison_target = comparison_target
        self.expect_empty = expect_empty

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        comparison_target_path = self.comparison_target.file_path(environment)
        if self.comparison_target.do_check_file_properties:
            error_message = check(comparison_target_path)
            if error_message:
                return pfh.new_pfh_fail(error_message)

        size = self.comparison_target.file_path(environment).stat().st_size
        if self.expect_empty:
            if size != 0:
                return pfh.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        else:
            if size == 0:
                return pfh.new_pfh_fail('File is empty')
        return pfh.new_pfh_pass()


def try_parse_content(comparison_target: ComparisonTarget,
                      target_transformer: TargetTransformer,
                      arguments: list) -> AssertPhaseInstruction:
    def _parse_empty(target: ComparisonTarget,
                     extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                'file/{}: Extra arguments: {}'.format(EMPTY_ARGUMENT,
                                                      str(extra_arguments)))
        return EmptinessCheckerInstruction(True, target)

    def _parse_non_empty(target: ComparisonTarget,
                         extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                'file/!{}: Extra arguments: {}'.format(EMPTY_ARGUMENT,
                                                       str(extra_arguments)))
        return EmptinessCheckerInstruction(False, target)

    def _parse_contents(target: ComparisonTarget,
                        extra_arguments: list) -> AssertPhaseInstruction:
        with_replaced_env_vars = False
        if extra_arguments and extra_arguments[0] == WITH_REPLACED_ENV_VARS_OPTION:
            with_replaced_env_vars = True
            del extra_arguments[0]
        comparison_source = _comparison_source(extra_arguments)
        if with_replaced_env_vars:
            return ContentCheckerWithTransformationInstruction(comparison_source,
                                                               target,
                                                               target_transformer)
        else:
            return ContentCheckerInstruction(comparison_source, target)

    def _comparison_source(last_arguments: list) -> ComparisonSource:
        if len(last_arguments) != 2:
            msg_header = 'file/contents: Invalid number of arguments (expecting two): '
            raise SingleInstructionInvalidArgumentException(msg_header + str(last_arguments))
        if last_arguments[0] == SOURCE_REL_HOME_OPTION:
            return ComparisonSourceForFileRelHome(last_arguments[1])
        elif last_arguments[0] == SOURCE_REL_CWD_OPTION:
            return ComparisonSourceForFileRelCwd(last_arguments[1])
        else:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Invalid argument: {}'.format(last_arguments[0]),
                               'Expecting one of: {}'.format(', '.join(SOURCE_REL_HOME_OPTION,
                                                                       SOURCE_REL_CWD_OPTION)),
                               ]))

    if arguments[0] == EMPTY_ARGUMENT:
        return _parse_empty(comparison_target, arguments[1:])
    elif arguments[:2] == ['!', EMPTY_ARGUMENT]:
        return _parse_non_empty(comparison_target, arguments[2:])
    else:
        return _parse_contents(comparison_target, arguments)
