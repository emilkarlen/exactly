import difflib
import filecmp
import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.instructions.utils.expectation_type import ExpectationType, from_is_negated
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import svh, pfh
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import HereDocOrFileRef
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator, \
    PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import tmp_text_file_containing

_EQUALITY_CHECK_EXPECTED_VALUE = 'equal'


class EqualsAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 negated: bool,
                 expected_contents: HereDocOrFileRef,
                 actual_contents: ComparisonActualFile,
                 actual_file_transformer: ActualFileTransformer):
        self._actual_value = actual_contents
        self._expected_contents = expected_contents
        self._actual_file_transformer = actual_file_transformer
        expectation_type = from_is_negated(negated)
        self._file_checker = _FileChecker(expectation_type,
                                          actual_contents.property_descriptor())
        self.validator_of_expected = ConstantSuccessValidator() if expected_contents.is_here_document else \
            FileRefCheckValidator(self._file_ref_check_for_expected())

    def symbol_usages(self) -> list:
        return self._expected_contents.symbol_usages + self._actual_value.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
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

        processed_actual_file_path = self._actual_file_transformer.transform(environment,
                                                                             os_services,
                                                                             actual_file_path)
        return self._file_checker.apply(environment,
                                        expected_file_path,
                                        processed_actual_file_path)

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
                           expected_file_path: pathlib.Path) -> list:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return list(diff)


class _FileChecker:
    def __init__(self,
                 expectation_type: ExpectationType,
                 property_descriptor: PropertyDescriptor):
        self._expectation_type = expectation_type
        self._property_descriptor = property_descriptor

    def apply(self,
              environment: i.InstructionEnvironmentForPostSdsStep,
              expected_file_path: pathlib.Path,
              processed_actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(processed_actual_file_path)
        expected_file_name = str(expected_file_path)
        files_are_equal = filecmp.cmp(actual_file_name, expected_file_name, shallow=False)

        if self._expectation_type is ExpectationType.POSITIVE:
            if not files_are_equal:
                diff_description = _file_diff_description(processed_actual_file_path,
                                                          expected_file_path)
                return self._new_failure(environment,
                                         diff_msg.actual_info_with_just_description_lines(diff_description))
        else:
            if files_are_equal:
                return self._new_failure(environment,
                                         diff_msg.actual_with_single_line_value(_EQUALITY_CHECK_EXPECTED_VALUE))
        return pfh.new_pfh_pass()

    def _new_failure(self,
                     environment: i.InstructionEnvironmentForPostSdsStep,
                     actual: diff_msg.ActualInfo,
                     ) -> pfh.PassOrFailOrHardError:
        failure_info = self._failure_info(environment, actual)
        msg = failure_info.render()
        return pfh.new_pfh_fail(msg)

    def _failure_info(self,
                      environment: i.InstructionEnvironmentForPostSdsStep,
                      actual: diff_msg.ActualInfo,
                      ) -> diff_msg.DiffFailureInfo:
        return diff_msg.DiffFailureInfo(
            self._property_descriptor.description(environment),
            self._expectation_type,
            _EQUALITY_CHECK_EXPECTED_VALUE,
            actual)
