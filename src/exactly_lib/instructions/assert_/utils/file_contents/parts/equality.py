import difflib
import filecmp
import pathlib
from typing import Sequence, List, Set, Optional

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import CONTENTS_ATTRIBUTE
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.program.string_or_file import StringOrFileRefResolver
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator, SingleStepValidator, ValidationStep
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg import ActualInfo
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import ExpectedValueResolver
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverOfParts
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor, ErrorMessageResolver, \
    ErrorMessageResolvingEnvironment, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherValue, StringMatcher
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import tmp_text_file_containing
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

_EQUALITY_CHECK_EXPECTED_VALUE = 'equals'


def assertion_part_via_string_matcher(expectation_type: ExpectationType,
                                      expected_contents: StringOrFileRefResolver) -> FileContentsAssertionPart:
    return StringMatcherAssertionPart(value_resolver(expectation_type, expected_contents))


def value_resolver(expectation_type: ExpectationType,
                   expected_contents: StringOrFileRefResolver) -> StringMatcherResolver:
    validator = _validator_of_expected(expected_contents)
    return StringMatcherResolverOfParts(
        expected_contents.symbol_usages,
        SingleStepValidator(ValidationStep.PRE_SDS,
                            validator),
        lambda symbols: EqualityStringMatcherValue(symbols,
                                                   expectation_type,
                                                   expected_contents,
                                                   validator)
    )


class EqualityStringMatcherValue(StringMatcherValue):
    def __init__(self,
                 symbols: SymbolTable,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrFileRefResolver,
                 validator: PreOrPostSdsValidator,
                 ):
        self._symbols = symbols
        self._expectation_type = expectation_type
        self._expected_contents = expected_contents
        self._validator = validator

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._expected_contents.resolve(self._symbols).resolving_dependencies()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return EqualityStringMatcher(PathResolvingEnvironmentPreOrPostSds(home_and_sds,
                                                                          self._symbols),
                                     self._expectation_type,
                                     self._expected_contents,
                                     self._validator)


class EqualityStringMatcher(StringMatcher):
    def __init__(self,
                 environment: PathResolvingEnvironmentPreOrPostSds,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrFileRefResolver,
                 validator: PreOrPostSdsValidator,
                 ):
        self._environment = environment
        self._expectation_type = expectation_type
        self._expected_contents = expected_contents
        self._validator = validator
        self._err_msg_constructor = _ErrorMessageResolverConstructor(expectation_type,
                                                                     expected_contents)

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        error_from_validation = self._do_post_setup_validation()
        if error_from_validation is not None:
            return error_from_validation

        expected_file_path = self._file_path_for_file_with_expected_contents()
        actual_file_path = model.transformed_file_path()

        files_are_equal = self._do_compare(expected_file_path, actual_file_path)
        return self._evaluate_comparison_result(files_are_equal,
                                                expected_file_path,
                                                actual_file_path,
                                                model.describer)

    def _file_path_for_file_with_expected_contents(self) -> pathlib.Path:
        expected_contents = self._expected_contents.resolve_value(self._environment.symbols)
        if expected_contents.is_file_ref:
            return expected_contents.file_ref_value.value_of_any_dependency(self._environment.home_and_sds)
        else:
            contents = expected_contents.string_value.value_of_any_dependency(self._environment.home_and_sds)
            return tmp_text_file_containing(contents,
                                            prefix='contents-',
                                            suffix='.txt',
                                            directory=str(self._environment.sds.internal_tmp_dir))

    @staticmethod
    def _do_compare(expected_file_path: pathlib.Path,
                    processed_actual_file_path: pathlib.Path) -> bool:
        actual_file_name = str(processed_actual_file_path)
        expected_file_name = str(expected_file_path)
        return filecmp.cmp(actual_file_name, expected_file_name, shallow=False)

    def _evaluate_comparison_result(self,
                                    files_are_equal: bool,
                                    expected_file_path: pathlib.Path,
                                    actual_file_path: pathlib.Path,
                                    checked_file_describer: FilePropertyDescriptorConstructor,
                                    ) -> Optional[ErrorMessageResolver]:
        if self._expectation_type is ExpectationType.POSITIVE:
            if not files_are_equal:
                diff_description = _file_diff_description(actual_file_path,
                                                          expected_file_path)
                return self._err_msg_constructor.construct(
                    checked_file_describer,
                    diff_msg.actual_with_just_description_lines(diff_description)
                )
        else:
            if files_are_equal:
                return self._err_msg_constructor.construct(
                    checked_file_describer,
                    diff_msg.actual_with_single_line_value(_EQUALITY_CHECK_EXPECTED_VALUE)
                )

        return None

    def _fail(self,
              checked_file_describer: FilePropertyDescriptorConstructor,
              actual_info: ActualInfo
              ) -> Optional[ErrorMessageResolver]:
        return _ErrorMessageResolver(self._expectation_type,
                                     self._expected_contents,
                                     checked_file_describer,
                                     actual_info)

    @property
    def option_description(self) -> str:
        return diff_msg.negation_str(self._expectation_type) + _EQUALITY_CHECK_EXPECTED_VALUE

    def _do_post_setup_validation(self) -> Optional[ErrorMessageResolver]:
        error_message = self._validator.validate_post_sds_if_applicable(self._environment)
        if error_message is None:
            return None
        else:
            return ConstantErrorMessageResolver(error_message)


def _validator_of_expected(expected_contents: StringOrFileRefResolver) -> PreOrPostSdsValidator:
    return expected_contents.validator__file_must_exist_as(FileType.REGULAR, True)


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> List[str]:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return list(diff)


class _ErrorMessageResolverConstructor:
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrFileRefResolver,
                 ):
        self._expected_contents = expected_contents
        self._expectation_type = expectation_type

    def construct(self,
                  checked_file: FilePropertyDescriptorConstructor,
                  actual_info: ActualInfo) -> ErrorMessageResolver:
        return _ErrorMessageResolver(self._expectation_type,
                                     self._expected_contents,
                                     checked_file,
                                     actual_info)


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrFileRefResolver,
                 checked_file_describer: FilePropertyDescriptorConstructor,
                 actual_info: ActualInfo
                 ):
        self._expected_contents = expected_contents
        self._expectation_type = expectation_type
        self._checked_file_describer = checked_file_describer
        self._actual_info = actual_info

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        description_of_actual_file = self._checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE)
        failure_info_resolver = DiffFailureInfoResolver(
            description_of_actual_file,
            self._expectation_type,
            ExpectedValueResolver(_EQUALITY_CHECK_EXPECTED_VALUE,
                                  self._expected_contents),
        )
        failure_info = failure_info_resolver.resolve(environment, self._actual_info)
        return failure_info.error_message()
