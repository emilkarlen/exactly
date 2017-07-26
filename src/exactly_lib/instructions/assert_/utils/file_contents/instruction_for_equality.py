import difflib
import filecmp
import os
import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.utils.arg_parse.parse_here_doc_or_file_ref import HereDocOrFileRef
from exactly_lib.instructions.utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh, pfh
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator, \
    PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import tmp_text_file_containing


class EqualsAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 negated: bool,
                 expected_contents: HereDocOrFileRef,
                 actual_contents: ComparisonActualFile,
                 actual_file_transformer: ActualFileTransformer):
        self._actual_value = actual_contents
        self._expected_contents = expected_contents
        self._actual_file_transformer = actual_file_transformer
        self._file_checker = _FileCheckerForNotEquals() if negated else _FileCheckerForEquals()
        self.validator_of_expected = ConstantSuccessValidator() if expected_contents.is_here_document else \
            FileRefCheckValidator(self._file_ref_check_for_expected())

    def symbol_usages(self) -> list:
        return self._expected_contents.symbol_usages + self._actual_value.symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        validator = PreOrPostSdsSvhValidationErrorValidator(self.validator_of_expected)
        return validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        if not self._expected_contents.is_here_document:
            failure_message = self.validator_of_expected.validate_post_sds_if_applicable(
                environment.path_resolving_environment)
            if failure_message:
                return pfh.new_pfh_fail(failure_message)
        expected_file_path = self._file_path_for_file_with_expected_contents(
            environment.path_resolving_environment_pre_or_post_sds)

        actual_file_path = self._actual_value.file_path(environment)
        failure_message = self._actual_value.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)

        display_actual_file_name = str(actual_file_path)
        processed_actual_file_path = self._actual_file_transformer.transform(environment,
                                                                             os_services,
                                                                             actual_file_path)
        return self._file_checker.apply(actual_file_path,
                                        expected_file_path,
                                        processed_actual_file_path,
                                        display_actual_file_name)

    def _file_path_for_file_with_expected_contents(self,
                                                   environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        expected_contents = self._expected_contents
        if expected_contents.is_here_document:
            contents = expected_contents.here_document.resolve_value_of_any_dependency(environment)
            return tmp_text_file_containing(contents,
                                            prefix='contents-',
                                            suffix='.txt',
                                            directory=str(environment.sds.tmp.internal_dir))
        else:
            return expected_contents.file_reference_resolver.resolve_value_of_any_dependency(environment)

    def _file_ref_check_for_expected(self) -> FileRefCheck:
        return FileRefCheck(self._expected_contents.file_reference_resolver,
                            must_exist_as(FileType.REGULAR))


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> str:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return os.linesep + ''.join(list(diff))


class _FileChecker:
    def apply(self,
              actual_file_path: pathlib.Path,
              expected_file_path: pathlib.Path,
              processed_actual_file_path: pathlib.Path,
              display_actual_file_name: str) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class _FileCheckerForEquals(_FileChecker):
    def apply(self,
              actual_file_path: pathlib.Path,
              expected_file_path: pathlib.Path,
              processed_actual_file_path: pathlib.Path,
              display_actual_file_name: str) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(processed_actual_file_path)
        expected_file_name = str(expected_file_path)
        if not filecmp.cmp(actual_file_name, expected_file_name, shallow=False):
            diff_description = _file_diff_description(processed_actual_file_path,
                                                      expected_file_path)
            return pfh.new_pfh_fail('Unexpected content in file: ' + display_actual_file_name +
                                    diff_description)
        return pfh.new_pfh_pass()


class _FileCheckerForNotEquals(_FileChecker):
    def apply(self,
              actual_file_path: pathlib.Path,
              expected_file_path: pathlib.Path,
              processed_actual_file_path: pathlib.Path,
              display_actual_file_name: str) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(processed_actual_file_path)
        expected_file_name = str(expected_file_path)
        if filecmp.cmp(actual_file_name, expected_file_name, shallow=False):
            return pfh.new_pfh_fail('Contents are equal.')
        return pfh.new_pfh_pass()
