import difflib
import filecmp
import pathlib
from typing import Sequence

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import CONTENTS_ATTRIBUTE, \
    FilePropertyDescriptorConstructor
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart, \
    FileToCheck
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg import ActualInfo
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import StringResolverOrFileRef, ExpectedValueResolver
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator, \
    PreOrPostSdsValidator, SingleStepValidator, ValidationStep
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import tmp_text_file_containing
from exactly_lib.util.logic_types import ExpectationType

_EQUALITY_CHECK_EXPECTED_VALUE = 'equals'


class EqualityContentsAssertionPart(FileContentsAssertionPart):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: StringResolverOrFileRef):
        self._expectation_type = expectation_type
        self._expected_contents = expected_contents
        self.validator_of_expected = _validator_of_expected(expected_contents)
        super().__init__(SingleStepValidator(ValidationStep.PRE_SDS,
                                             self.validator_of_expected))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._expected_contents.symbol_usages

    def check(self,
              environment: i.InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:

        self._do_post_setup_validation(environment)

        expected_file_path = self._file_path_for_file_with_expected_contents(
            environment.path_resolving_environment_pre_or_post_sds)

        transformed_file_path = file_to_check.transformed_file_path()
        files_are_equal = self._do_compare(expected_file_path, transformed_file_path)

        self._do_check_comparison_result(environment,
                                         files_are_equal,
                                         expected_file_path,
                                         transformed_file_path,
                                         file_to_check.describer)
        return file_to_check

    def _do_check_comparison_result(self,
                                    environment: i.InstructionEnvironmentForPostSdsStep,
                                    files_are_equal: bool,
                                    expected_file_path: pathlib.Path,
                                    actual_file_path: pathlib.Path,
                                    checked_file_describer: FilePropertyDescriptorConstructor,
                                    ):
        if self._expectation_type is ExpectationType.POSITIVE:
            if not files_are_equal:
                diff_description = _file_diff_description(actual_file_path,
                                                          expected_file_path)
                self._fail(environment,
                           checked_file_describer,
                           diff_msg.actual_with_just_description_lines(diff_description))
        else:
            if files_are_equal:
                self._fail(environment,
                           checked_file_describer,
                           diff_msg.actual_with_single_line_value(_EQUALITY_CHECK_EXPECTED_VALUE))

    @staticmethod
    def _do_compare(expected_file_path: pathlib.Path,
                    processed_actual_file_path: pathlib.Path):
        actual_file_name = str(processed_actual_file_path)
        expected_file_name = str(expected_file_path)
        files_are_equal = filecmp.cmp(actual_file_name, expected_file_name, shallow=False)
        return files_are_equal

    def _do_post_setup_validation(self, environment: i.InstructionEnvironmentForPostSdsStep):
        failure_message = self.validator_of_expected.validate_post_sds_if_applicable(
            environment.path_resolving_environment)
        if failure_message:
            raise PfhFailException(failure_message)

    def _file_path_for_file_with_expected_contents(self,
                                                   environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        expected_contents = self._expected_contents
        if not expected_contents.is_file_ref:
            contents = expected_contents.string_resolver.resolve_value_of_any_dependency(environment)
            return tmp_text_file_containing(contents,
                                            prefix='contents-',
                                            suffix='.txt',
                                            directory=str(environment.sds.tmp.internal_dir))
        else:
            return expected_contents.file_reference_resolver.resolve_value_of_any_dependency(environment)

    def _fail(self,
              environment: i.InstructionEnvironmentForPostSdsStep,
              checked_file_describer: FilePropertyDescriptorConstructor,
              actual_info: ActualInfo
              ):
        failure_info = self._failure_resolver(checked_file_describer).resolve(environment, actual_info)
        raise PfhFailException(failure_info.error_message())

    def _failure_resolver(self, checked_file_describer: FilePropertyDescriptorConstructor) -> DiffFailureInfoResolver:
        description_of_actual_file = checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE)
        return DiffFailureInfoResolver(
            description_of_actual_file,
            self._expectation_type,
            ExpectedValueResolver(_EQUALITY_CHECK_EXPECTED_VALUE,
                                  self._expected_contents),
        )


def _validator_of_expected(expected_contents: StringResolverOrFileRef) -> PreOrPostSdsValidator:
    if not expected_contents.is_file_ref:
        return ConstantSuccessValidator()
    file_ref_check = FileRefCheck(expected_contents.file_reference_resolver,
                                  must_exist_as(FileType.REGULAR))
    return FileRefCheckValidator(file_ref_check)


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> list:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return list(diff)
