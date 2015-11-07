import difflib
import filecmp
import os
import pathlib

from shellcheck_lib.execution import environment_variables
from shellcheck_lib.general import file_utils
from shellcheck_lib.general.file_utils import ensure_parent_directory_does_exist
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.instructions.assert_phase.utils import instruction_utils
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_file_ref import SOURCE_REL_HOME_OPTION, SOURCE_REL_CWD_OPTION, \
    SOURCE_REL_TMP_OPTION
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.os_services import OsServices

WITH_REPLACED_ENV_VARS_OPTION = '--with-replaced-env-vars'
EMPTY_ARGUMENT = 'empty'


class ComparisonSource:
    def __init__(self,
                 check_during_validation: bool,
                 file_name: str):
        self.check_during_validation = check_during_validation
        self.file_name = file_name

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


def parse_source_file_argument(arguments: list) -> (ComparisonSource, list):
    if len(arguments) < 2:
        msg_header = 'file/contents: Invalid number of arguments (expecting at least two): '
        raise SingleInstructionInvalidArgumentException(msg_header + str(arguments))
    option = arguments[0]
    if option == SOURCE_REL_HOME_OPTION:
        return ComparisonSourceForFileRelHome(arguments[1]), arguments[2:]
    elif option == SOURCE_REL_CWD_OPTION:
        return ComparisonSourceForFileRelCwd(arguments[1]), arguments[2:]
    elif option == SOURCE_REL_TMP_OPTION:
        return ComparisonSourceForFileRelTmpUser(arguments[1]), arguments[2:]
    else:
        raise SingleInstructionInvalidArgumentException(
            lines_content(['Invalid argument: {}'.format(arguments[0]),
                           'Expecting one of: {}'.format(', '.join([SOURCE_REL_HOME_OPTION,
                                                                    SOURCE_REL_TMP_OPTION,
                                                                    SOURCE_REL_CWD_OPTION])),
                           ]))


class ComparisonTarget:
    def __init__(self, do_check_file_properties: bool):
        self.do_check_file_properties = do_check_file_properties

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


def parse_target_file_argument(arguments: list) -> (ComparisonTarget, list):
    def ensure_have_at_least_two_arguments_for_option(option: str):
        if len(arguments) < 2:
            raise SingleInstructionInvalidArgumentException('{} requires a FILE argument'.format(option))

    if len(arguments) < 1:
        msg_header = 'Invalid number of arguments (expecting at least one): '
        raise SingleInstructionInvalidArgumentException(msg_header + str(arguments))
    first_argument = arguments[0]
    if first_argument == SOURCE_REL_CWD_OPTION:
        ensure_have_at_least_two_arguments_for_option(SOURCE_REL_CWD_OPTION)
        return ActComparisonTargetRelCwd(arguments[1]), arguments[2:]
    elif first_argument == SOURCE_REL_TMP_OPTION:
        ensure_have_at_least_two_arguments_for_option(SOURCE_REL_TMP_OPTION)
        return ActComparisonTargetRelTmpUser(arguments[1]), arguments[2:]
    return ActComparisonTargetRelCwd(first_argument), arguments[1:]


class ComparisonSourceForFileRelHome(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.home_directory / self.file_name


class ComparisonSourceForFileRelCwd(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return pathlib.Path(self.file_name)


class ComparisonSourceForFileRelTmpUser(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.tmp.user_dir / self.file_name


class ActComparisonTargetRelCwd(ComparisonTarget):
    def __init__(self,
                 file_name: str):
        super().__init__(True)
        self.file_name = file_name

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return pathlib.Path(self.file_name)


class ActComparisonTargetRelTmpUser(ComparisonTarget):
    def __init__(self,
                 file_name: str):
        super().__init__(True)
        self.file_name = file_name

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.tmp.user_dir / self.file_name


class StdoutComparisonTarget(ComparisonTarget):
    def __init__(self):
        super().__init__(False)

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.result.stdout_file


class StderrComparisonTarget(ComparisonTarget):
    def __init__(self):
        super().__init__(False)

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.result.stderr_file


def check(file_path: pathlib.Path) -> str:
    if not file_path.exists():
        return 'File does not exist: ' + str(file_path)
    if not file_path.is_file():
        return 'Not a regular file: ' + str(file_path)
    return None


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
            diff_description = _file_diff_description(comparison_target_file_path,
                                                      comparison_source_file_path)
            return pfh.new_pfh_fail('Unexpected content in file: ' + display_target_file_name +
                                    diff_description)
        return pfh.new_pfh_pass()

    def _get_comparison_target_file_path(self,
                                         target_file_path: pathlib.Path,
                                         environment: i.GlobalEnvironmentForPostEdsPhase,
                                         os_services: OsServices) -> pathlib.Path:
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
        src_file_path = target_file_path
        dst_file_path = self._dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        env_vars_to_replace = environment_variables.replaced(environment.home_directory,
                                                             environment.eds)
        self._replace_env_vars_and_write_result_to_dst(env_vars_to_replace,
                                                       src_file_path,
                                                       dst_file_path)
        return dst_file_path

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
        (comparison_source, remaining_arguments) = parse_source_file_argument(extra_arguments)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException(
                lines_content('Superfluous arguments: {}'.format(remaining_arguments)))

        if with_replaced_env_vars:
            return ContentCheckerWithTransformationInstruction(comparison_source,
                                                               target,
                                                               target_transformer)
        else:
            return ContentCheckerInstruction(comparison_source, target)

    if arguments[0] == EMPTY_ARGUMENT:
        return _parse_empty(comparison_target, arguments[1:])
    elif arguments[:2] == ['!', EMPTY_ARGUMENT]:
        return _parse_non_empty(comparison_target, arguments[2:])
    else:
        return _parse_contents(comparison_target, arguments)


def _file_diff_description(comparison_target_file_path: pathlib.Path,
                           comparison_source_file_path: pathlib.Path) -> str:
    source_lines = file_utils.lines_of(comparison_source_file_path)
    target_lines = file_utils.lines_of(comparison_target_file_path)
    diff = difflib.unified_diff(source_lines,
                                target_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return os.linesep + ''.join(list(diff))
