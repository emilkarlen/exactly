import difflib
import filecmp
import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.utils.documentation import documentation_text
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import svh, pfh
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.err_msg.path_description import path_value_with_relativity_name_prefix
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.test_case_utils.file_transformer.actual_file_transformer import ActualFileTransformerResolver
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import HereDocOrFileRef
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator, \
    PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.util import file_utils
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib.util.file_utils import tmp_text_file_containing

_EQUALITY_CHECK_EXPECTED_VALUE = 'equals'


class EqualsAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: HereDocOrFileRef,
                 actual_contents: ComparisonActualFile,
                 actual_file_transformer_resolver: ActualFileTransformerResolver):
        self._actual_value = actual_contents
        self._expected_contents = expected_contents
        self._actual_file_transformer_resolver = actual_file_transformer_resolver
        failure_resolver = DiffFailureInfoResolver(
            actual_contents.property_descriptor(),
            expectation_type,
            ExpectedValueResolver(expected_contents),
        )
        self._file_checker = _FileChecker(expectation_type,
                                          failure_resolver)
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

        failure_message = self._actual_value.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)

        actual_file_path = self._actual_value.file_path(environment)
        actual_file_transformer = self._actual_file_transformer_resolver.resolve(environment.symbols)
        processed_actual_file_path = actual_file_transformer.transform(environment,
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
                 failure_resolver: DiffFailureInfoResolver):
        self._expectation_type = expectation_type
        self._failure_resolver = failure_resolver

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
                return self._failure_resolver.resolve(
                    environment,
                    diff_msg.actual_with_just_description_lines(
                        diff_description)).as_pfh_fail()
        else:
            if files_are_equal:
                return self._failure_resolver.resolve(
                    environment,
                    diff_msg.actual_with_single_line_value(
                        _EQUALITY_CHECK_EXPECTED_VALUE)).as_pfh_fail()
        return pfh.new_pfh_pass()


class ExpectedValueResolver(diff_msg_utils.ExpectedValueResolver):
    def __init__(self, expected_contents: HereDocOrFileRef):
        self.expected_contents = expected_contents

    def resolve(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return _EQUALITY_CHECK_EXPECTED_VALUE + ' ' + self._expected_obj_description(environment)

    def _expected_obj_description(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        if self.expected_contents.here_document:
            return documentation_text.HERE_DOCUMENT.name
        if self.expected_contents.is_file_ref:
            resolving_env = environment.path_resolving_environment_pre_or_post_sds
            path_value = self.expected_contents.file_reference_resolver.resolve(resolving_env.symbols)
            path_description = path_value_with_relativity_name_prefix(path_value,
                                                                      resolving_env.home_and_sds,
                                                                      pathlib.Path.cwd())
            return 'file ' + path_description
