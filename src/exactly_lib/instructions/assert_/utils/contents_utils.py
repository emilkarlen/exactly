import difflib
import filecmp
import os
import pathlib

from exactly_lib import program_info
from exactly_lib.cli.util.cli_argument_syntax import long_option_name
from exactly_lib.execution import environment_variables
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_here_doc_or_file_ref import HereDocOrFileRef
from exactly_lib.instructions.utils.file_properties import must_exist_as, FileType
from exactly_lib.instructions.utils.file_ref import FileRef
from exactly_lib.instructions.utils.file_ref_check import FileRefCheck, \
    pre_or_post_eds_failure_message_or_none, FileRefCheckValidator
from exactly_lib.instructions.utils.pre_or_post_validation import ConstantSuccessValidator, \
    PreOrPostEdsSvhValidationErrorValidator
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, HomeAndEds, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util import file_utils
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist, tmp_text_file_containing
from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = long_option_name(WITH_REPLACED_ENV_VARS_OPTION_NAME.long)

EMPTY_ARGUMENT = 'empty'
NOT_ARGUMENT = '!'


def with_replaced_env_vars_help(checked_file: str) -> list:
    header_text = """\
    Every occurrence of a path that matches any of the {program_name} environment variables
    in {checked_file} is replaced with the name of the matching variable.
    (Variable values are replaced with variable names.)


    These environment variables are:
    """.format(program_name=formatting.program_name(program_info.PROGRAM_NAME),
               option=WITH_REPLACED_ENV_VARS_OPTION,
               checked_file=checked_file)
    variables_list = [docs.simple_header_only_list(sorted(environment_variables.ALL_REPLACED_ENV_VARS),
                                                   docs.lists.ListType.VARIABLE_LIST)]
    return normalize_and_parse(header_text) + variables_list


class ComparisonActualFile:
    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        """
        :return: None iff there is no failure.
        """
        raise NotImplementedError()

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        raise NotImplementedError()


class ActComparisonActualFileForFileRef(ComparisonActualFile):
    def __init__(self,
                 file_ref: FileRef):
        self.file_ref = file_ref

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return pre_or_post_eds_failure_message_or_none(FileRefCheck(self.file_ref,
                                                                    must_exist_as(FileType.REGULAR)),
                                                       environment.home_and_eds)

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return self.file_ref.file_path_pre_or_post_eds(environment.home_and_eds)


class ActComparisonActualFileForStdFileBase(ComparisonActualFile):
    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return None


class StdoutComparisonTarget(ActComparisonActualFileForStdFileBase):
    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return environment.eds.result.stdout_file


class StderrComparisonTarget(ActComparisonActualFileForStdFileBase):
    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return environment.eds.result.stderr_file


class ContentCheckerInstructionBase(AssertPhaseInstruction):
    def __init__(self,
                 expected_contents: HereDocOrFileRef,
                 actual_contents: ComparisonActualFile):
        self._actual_value = actual_contents
        self._expected_contents = expected_contents
        self.validator_of_expected = ConstantSuccessValidator() if expected_contents.is_here_document else \
            FileRefCheckValidator(self._file_ref_check_for_expected())

    def validate_pre_eds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        validator = PreOrPostEdsSvhValidationErrorValidator(self.validator_of_expected)
        return validator.validate_pre_eds_if_applicable(environment.home_directory)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        if not self._expected_contents.is_here_document:
            failure_message = self.validator_of_expected.validate_post_eds_if_applicable(environment.home_and_eds.eds)
            if failure_message:
                return pfh.new_pfh_fail(failure_message)
        expected_file_path = self._file_path_for_file_with_expected_contents(environment.home_and_eds)

        actual_file_path = self._actual_value.file_path(environment)
        failure_message = self._actual_value.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)

        display_actual_file_name = str(actual_file_path)
        expected_file_name = str(expected_file_path)
        processed_actual_file_path = self._get_processed_actual_file_path(actual_file_path,
                                                                          environment,
                                                                          os_services)
        actual_file_name = str(processed_actual_file_path)
        if not filecmp.cmp(actual_file_name, expected_file_name, shallow=False):
            diff_description = _file_diff_description(processed_actual_file_path,
                                                      expected_file_path)
            return pfh.new_pfh_fail('Unexpected content in file: ' + display_actual_file_name +
                                    diff_description)
        return pfh.new_pfh_pass()

    def _file_path_for_file_with_expected_contents(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        if self._expected_contents.is_here_document:
            contents = lines_content(self._expected_contents.here_document)
            return tmp_text_file_containing(contents,
                                            prefix='contents-',
                                            suffix='.txt',
                                            directory=str(home_and_eds.eds.tmp.internal_dir))
        else:
            return self._expected_contents.file_reference.file_path_pre_or_post_eds(home_and_eds)

    def _file_ref_check_for_expected(self) -> FileRefCheck:
        return FileRefCheck(self._expected_contents.file_reference,
                            must_exist_as(FileType.REGULAR))

    def _get_processed_actual_file_path(self,
                                        actual_file_path: pathlib.Path,
                                        environment: i.InstructionEnvironmentForPostSdsStep,
                                        os_services: OsServices) -> pathlib.Path:
        raise NotImplementedError()


class ContentCheckerInstruction(ContentCheckerInstructionBase):
    def __init__(self,
                 expected_contents: HereDocOrFileRef,
                 actual_contents: ComparisonActualFile):
        super().__init__(expected_contents, actual_contents)

    def _get_processed_actual_file_path(self,
                                        actual_file_path: pathlib.Path,
                                        environment: i.InstructionEnvironmentForPostSdsStep,
                                        os_services: OsServices) -> pathlib.Path:
        return actual_file_path


class ActualFileTransformer:
    def replace_env_vars(self,
                         environment: InstructionEnvironmentForPostSdsStep,
                         os_services: OsServices,
                         actual_file_path: pathlib.Path) -> pathlib.Path:
        src_file_path = actual_file_path
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
                       environment: InstructionEnvironmentForPostSdsStep,
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
                 expected_contents: HereDocOrFileRef,
                 actual_contents: ComparisonActualFile,
                 actual_file_transformer: ActualFileTransformer):
        super().__init__(expected_contents, actual_contents)
        self.actual_file_transformer = actual_file_transformer

    def _get_processed_actual_file_path(self,
                                        actual_file_path: pathlib.Path,
                                        environment: i.InstructionEnvironmentForPostSdsStep,
                                        os_services: OsServices) -> pathlib.Path:
        return self.actual_file_transformer.replace_env_vars(environment,
                                                             os_services,
                                                             actual_file_path)


class EmptinessCheckerInstruction(AssertPhaseInstruction):
    def __init__(self,
                 expect_empty: bool,
                 actual_file: ComparisonActualFile):
        self.actual_file = actual_file
        self.expect_empty = expect_empty

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = self.actual_file.file_check_failure(environment)
        if failure_message:
            return pfh.new_pfh_fail(failure_message)

        size = self.actual_file.file_path(environment).stat().st_size
        if self.expect_empty:
            if size != 0:
                return pfh.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        else:
            if size == 0:
                return pfh.new_pfh_fail('File is empty')
        return pfh.new_pfh_pass()


def try_parse_content(actual_file: ComparisonActualFile,
                      actual_file_transformer: ActualFileTransformer,
                      arguments: list,
                      source: SingleInstructionParserSource) -> AssertPhaseInstruction:
    def _parse_empty(actual: ComparisonActualFile,
                     extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                'file/{}: Extra arguments: {}'.format(EMPTY_ARGUMENT,
                                                      str(extra_arguments)))
        return EmptinessCheckerInstruction(True, actual)

    def _parse_non_empty(actual: ComparisonActualFile,
                         extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                'file/!{}: Extra arguments: {}'.format(EMPTY_ARGUMENT,
                                                       str(extra_arguments)))
        return EmptinessCheckerInstruction(False, actual)

    def _parse_contents(actual: ComparisonActualFile,
                        extra_arguments: list) -> AssertPhaseInstruction:
        with_replaced_env_vars = False
        if extra_arguments and matches(WITH_REPLACED_ENV_VARS_OPTION_NAME, extra_arguments[0]):
            with_replaced_env_vars = True
            del extra_arguments[0]
        (here_doc_or_file_ref_for_expected, remaining_arguments) = parse_here_doc_or_file_ref.parse(extra_arguments,
                                                                                                    source)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Superfluous arguments: {}'.format(remaining_arguments)]))

        if with_replaced_env_vars:
            return ContentCheckerWithTransformationInstruction(here_doc_or_file_ref_for_expected,
                                                               actual,
                                                               actual_file_transformer)
        else:
            return ContentCheckerInstruction(here_doc_or_file_ref_for_expected, actual)

    if arguments[0] == EMPTY_ARGUMENT:
        return _parse_empty(actual_file, arguments[1:])
    elif arguments[:2] == [NOT_ARGUMENT, EMPTY_ARGUMENT]:
        return _parse_non_empty(actual_file, arguments[2:])
    else:
        return _parse_contents(actual_file, arguments)


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> str:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return os.linesep + ''.join(list(diff))
