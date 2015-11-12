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
from shellcheck_lib.instructions.utils.file_properties import must_exist_as, FileType
from shellcheck_lib.instructions.utils.file_ref import FileRef
from shellcheck_lib.instructions.utils.file_ref_check import post_eds_validate, FileRefCheck, \
    post_eds_failure_message_or_none
from shellcheck_lib.instructions.utils.parse_file_ref import parse_relative_file_argument, parse_non_home_file_ref
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.os_services import OsServices

WITH_REPLACED_ENV_VARS_OPTION = '--with-replaced-env-vars'
EMPTY_ARGUMENT = 'empty'


class ComparisonTarget:
    def file_check_failure(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> str:
        """
        :return: None iff there is no failure.
        """
        raise NotImplementedError()

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


def parse_target_file_argument(arguments: list) -> (ComparisonTarget, list):
    if len(arguments) < 1:
        msg_header = 'Invalid number of arguments (expecting at least one): '
        raise SingleInstructionInvalidArgumentException(msg_header + str(arguments))
    (file_ref, remaining_arguments) = parse_non_home_file_ref(arguments)
    return ActComparisonTargetForFileRef(file_ref), remaining_arguments


class ActComparisonTargetForFileRef(ComparisonTarget):
    def __init__(self,
                 file_ref: FileRef):
        self.file_ref = file_ref

    def file_check_failure(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> str:
        return post_eds_failure_message_or_none(FileRefCheck(self.file_ref,
                                                             must_exist_as(FileType.REGULAR)),
                                                environment)

    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return self.file_ref.file_path_post_eds(environment.home_and_eds)


class ActComparisonTargetForStdFileBase(ComparisonTarget):
    def file_check_failure(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> str:
        return None


class StdoutComparisonTarget(ActComparisonTargetForStdFileBase):
    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.result.stdout_file


class StderrComparisonTarget(ActComparisonTargetForStdFileBase):
    def file_path(self, environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.result.stderr_file


class ContentCheckerInstructionBase(AssertPhaseInstruction):
    def __init__(self,
                 expected_contents: FileRef,
                 comparison_target: ComparisonTarget):
        self.comparison_target = comparison_target
        self._expected_contents = expected_contents

    def validate(self,
                 environment: i.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        if self._expected_contents.exists_pre_eds:
            return post_eds_validate(self._file_ref_check_for_expected(),
                                     environment)
        else:
            return svh.new_svh_success()

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = post_eds_failure_message_or_none(self._file_ref_check_for_expected(),
                                                           environment)
        if failure_message:
            return pfh.new_pfh_fail(failure_message)
        file_path_for_expected = self._expected_contents.file_path_post_eds(environment.home_and_eds)

        comparison_target_path = self.comparison_target.file_path(environment)
        failure_message = self.comparison_target.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)

        display_target_file_name = str(comparison_target_path)
        comparison_source_file_name = str(file_path_for_expected)
        comparison_target_file_path = self._get_comparison_target_file_path(comparison_target_path,
                                                                            environment,
                                                                            os_services)
        comparison_target_file_name = str(comparison_target_file_path)
        if not filecmp.cmp(comparison_target_file_name, comparison_source_file_name, shallow=False):
            diff_description = _file_diff_description(comparison_target_file_path,
                                                      file_path_for_expected)
            return pfh.new_pfh_fail('Unexpected content in file: ' + display_target_file_name +
                                    diff_description)
        return pfh.new_pfh_pass()

    def _file_ref_check_for_expected(self):
        return FileRefCheck(self._expected_contents,
                            must_exist_as(FileType.REGULAR))

    def _get_comparison_target_file_path(self,
                                         target_file_path: pathlib.Path,
                                         environment: i.GlobalEnvironmentForPostEdsPhase,
                                         os_services: OsServices) -> pathlib.Path:
        raise NotImplementedError()


class ContentCheckerInstruction(ContentCheckerInstructionBase):
    def __init__(self,
                 expected_contents: FileRef,
                 comparison_target: ComparisonTarget):
        super().__init__(expected_contents, comparison_target)

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
                 expected_contents: FileRef,
                 comparison_target: ComparisonTarget,
                 target_transformer: TargetTransformer):
        super().__init__(expected_contents, comparison_target)
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
        failure_message = self.comparison_target.file_check_failure(environment)
        if failure_message:
            return pfh.new_pfh_fail(failure_message)

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
        (file_ref_for_expected, remaining_arguments) = parse_relative_file_argument(extra_arguments)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException(
                lines_content('Superfluous arguments: {}'.format(remaining_arguments)))

        if with_replaced_env_vars:
            return ContentCheckerWithTransformationInstruction(file_ref_for_expected,
                                                               target,
                                                               target_transformer)
        else:
            return ContentCheckerInstruction(file_ref_for_expected, target)

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
