import difflib
import filecmp
import pathlib
from typing import List, Set, Optional

from exactly_lib.definitions.actual_file_attributes import CONTENTS_ATTRIBUTE
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.program.string_or_file import StringOrFileRefResolver, SourceType
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator, SingleStepValidator, ValidationStep, \
    PreOrPostSdsValidatorPrimitive, FixedPreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg import ActualInfo
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import ExpectedValueResolver
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverFromParts
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor, ErrorMessageResolver, \
    ErrorMessageResolvingEnvironment, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.program.string_or_file_ref_values import StringOrPath
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcher
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import tmp_text_file_containing, TmpDirFileSpace
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

_EQUALITY_CHECK_EXPECTED_VALUE = 'equals'

_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS = 'EXPECTED'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_file_ref.CONFIGURATION


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    token_parser.require_has_valid_head_token(_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS)
    expected_contents = parse_here_doc_or_file_ref.parse_from_token_parser(
        token_parser,
        EXPECTED_FILE_REL_OPT_ARG_CONFIG)
    if expected_contents.source_type is not SourceType.HERE_DOC:
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

    return value_resolver(
        expectation_type,
        expected_contents,
    )


def value_resolver(expectation_type: ExpectationType,
                   expected_contents: StringOrFileRefResolver) -> StringMatcherResolver:
    validator = _validator_of_expected(expected_contents)
    error_message_constructor = _ErrorMessageResolverConstructor(expectation_type,
                                                                 ExpectedValueResolver(_EQUALITY_CHECK_EXPECTED_VALUE,
                                                                                       expected_contents))

    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:
        return EqualityStringMatcher(
            expectation_type,
            expected_contents.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds),
            error_message_constructor,
            FixedPreOrPostSdsValidator(environment, validator)
        )

    def get_resolving_dependencies(symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
        return expected_contents.resolve(symbols).resolving_dependencies()

    return StringMatcherResolverFromParts(
        expected_contents.references,
        SingleStepValidator(ValidationStep.PRE_SDS,
                            validator),
        get_resolving_dependencies,
        get_matcher,
    )


class _ErrorMessageResolverConstructor:
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_value: ExpectedValueResolver,
                 ):
        self._expectation_type = expectation_type
        self._expected_value = expected_value

    def construct(self,
                  checked_file: FilePropertyDescriptorConstructor,
                  actual_info: ActualInfo) -> ErrorMessageResolver:
        return _ErrorMessageResolver(self._expectation_type,
                                     self._expected_value,
                                     checked_file,
                                     actual_info)


class EqualityStringMatcher(StringMatcher):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrPath,
                 error_message_constructor: _ErrorMessageResolverConstructor,
                 validator: PreOrPostSdsValidatorPrimitive,
                 ):
        self._expectation_type = expectation_type
        self._expected_contents = expected_contents
        self._validator = validator
        self._err_msg_constructor = error_message_constructor

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        error_from_validation = self._do_post_setup_validation()
        if error_from_validation is not None:
            return error_from_validation

        expected_file_path = self._file_path_for_file_with_expected_contents(model.tmp_file_space)
        actual_file_path = model.transformed_file_path()

        files_are_equal = self._do_compare(expected_file_path, actual_file_path)
        return self._evaluate_comparison_result(files_are_equal,
                                                expected_file_path,
                                                actual_file_path,
                                                model.describer)

    def _file_path_for_file_with_expected_contents(self, tmp_file_space: TmpDirFileSpace) -> pathlib.Path:
        if self._expected_contents.is_path:
            return self._expected_contents.file_ref_value
        else:
            contents = self._expected_contents.string_value
            return tmp_text_file_containing(contents,
                                            prefix='contents-',
                                            suffix='.txt',
                                            directory=str(tmp_file_space.new_path_as_existing_dir()))

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

    @property
    def option_description(self) -> str:
        return diff_msg.negation_str(self._expectation_type) + _EQUALITY_CHECK_EXPECTED_VALUE

    def _do_post_setup_validation(self) -> Optional[ErrorMessageResolver]:
        error_message = self._validator.validate_post_sds_if_applicable()
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


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_value: ExpectedValueResolver,
                 checked_file_describer: FilePropertyDescriptorConstructor,
                 actual_info: ActualInfo
                 ):
        self._expected_value = expected_value
        self._expectation_type = expectation_type
        self._checked_file_describer = checked_file_describer
        self._actual_info = actual_info

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        description_of_actual_file = self._checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE)
        failure_info_resolver = DiffFailureInfoResolver(
            description_of_actual_file,
            self._expectation_type,
            self._expected_value,
        )
        failure_info = failure_info_resolver.resolve(environment, self._actual_info)
        return failure_info.error_message()
