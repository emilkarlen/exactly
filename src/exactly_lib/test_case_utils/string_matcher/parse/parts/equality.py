import difflib
import filecmp
import pathlib
from typing import List, Optional, Iterable

from exactly_lib.definitions.actual_file_attributes import CONTENTS_ATTRIBUTE
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_or_path import StringOrPathSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case.validation.sdv_validation import PreOrPostSdsValidatorPrimitive
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details, custom_renderers
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg import ActualInfo
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver, ExpectedValueResolver
from exactly_lib.test_case_utils.err_msg2 import env_dep_texts
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.test_case_utils.parse import parse_here_doc_or_path
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.base_class import StringMatcherImplBase
from exactly_lib.test_case_utils.string_matcher.sdvs import string_matcher_sdv_from_parts_2
from exactly_lib.type_system.data.string_or_path_ddvs import StringOrPath, StringOrPathDdv
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, MatcherAdv, MODEL
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherDdv
from exactly_lib.util import file_utils
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.file_utils import tmp_text_file_containing, TmpDirFileSpace
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.strings import StringConstructor
from exactly_lib.util.symbol_table import SymbolTable

_EQUALITY_CHECK_EXPECTED_VALUE = 'equals'

_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS = 'EXPECTED'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_path.CONFIGURATION


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    token_parser.require_has_valid_head_token(_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS)
    expected_contents = parse_here_doc_or_path.parse_from_token_parser(
        token_parser,
        EXPECTED_FILE_REL_OPT_ARG_CONFIG,
        consume_last_here_doc_line=False)

    return value_sdv(
        expectation_type,
        expected_contents,
    )


def value_sdv(expectation_type: ExpectationType,
              expected_contents: StringOrPathSdv) -> StringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> StringMatcherDdv:
        expected_contents_ddv = expected_contents.resolve(symbols)

        return EqualityStringMatcherDdv(
            expectation_type,
            expected_contents_ddv,
            _validator_of_expected(expected_contents_ddv),
        )

    return string_matcher_sdv_from_parts_2(expected_contents.references, get_ddv)


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


class EqualityStringMatcherDdv(MatcherDdv[FileToCheck]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrPathDdv,
                 validator: DdvValidator,
                 ):
        super().__init__()
        self._expectation_type = expectation_type
        self._expected_contents = expected_contents
        self._validator = validator
        self._renderer_of_expected_value = custom_details.StringOrPath(expected_contents)
        self._expected_detail_renderer = custom_details.expected(self._renderer_of_expected_value)

    def structure(self) -> StructureRenderer:
        return EqualityStringMatcher.new_structure_tree(
            self._expectation_type,
            custom_details.StringOrPathValue(self._expected_contents),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        expected_contents = self._expected_contents.value_of_any_dependency(tcds)
        return advs.ConstantMatcherAdv(
            EqualityStringMatcher(
                self._expectation_type,
                expected_contents,
                _ErrorMessageResolverConstructor(
                    self._expectation_type,
                    parse_here_doc_or_path.ExpectedValueResolver(_EQUALITY_CHECK_EXPECTED_VALUE,
                                                                 expected_contents)
                ),
                ddv_validators.FixedPreOrPostSdsValidator(tcds, self._validator),
            )
        )


class EqualityStringMatcher(StringMatcherImplBase):
    NAME = matcher_options.EQUALS_ARGUMENT

    @staticmethod
    def new_structure_tree(expectation_type: ExpectationType,
                           expected_contents: DetailsRenderer) -> StructureRenderer:
        equality_node = renderers.header_and_detail(
            EqualityStringMatcher.NAME,
            expected_contents,
        )

        return custom_renderers.positive_or_negative(expectation_type, equality_node)

    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_contents: StringOrPath,
                 error_message_constructor: _ErrorMessageResolverConstructor,
                 validator: PreOrPostSdsValidatorPrimitive,
                 ):
        super().__init__()
        self._expectation_type = expectation_type
        self._expected_contents = expected_contents
        self._validator = validator
        self._err_msg_constructor = error_message_constructor
        self._renderer_of_expected_value = custom_details.StringOrPath(expected_contents)
        self._expected_detail_renderer = custom_details.expected(self._renderer_of_expected_value)

    @property
    def name(self) -> str:
        return matcher_options.EQUALS_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return EqualityStringMatcher.new_structure_tree(
            self._expectation_type,
            custom_details.StringOrPath(self._expected_contents),
        )

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        error_from_validation = self._do_post_setup_validation__old()
        if error_from_validation is not None:
            return error_from_validation

        expected_file_path = self._file_path_for_file_with_expected_contents(model.tmp_file_space)
        actual_file_path = model.transformed_file_path()

        files_are_equal = self._do_compare(expected_file_path, actual_file_path)
        return self._evaluate_comparison_result(files_are_equal,
                                                expected_file_path,
                                                actual_file_path,
                                                model.describer)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        if self._expectation_type is ExpectationType.NEGATIVE:
            positive_matcher = EqualityStringMatcher(ExpectationType.POSITIVE,
                                                     self._expected_contents,
                                                     self._err_msg_constructor,
                                                     self._validator)
            return combinator_matchers.Negation(positive_matcher).matches_w_trace(model)
        else:
            return self._matches_positive(model)

    def _matches_positive(self, model: FileToCheck) -> MatchingResult:
        error_message = self._validator.validate_post_sds_if_applicable()
        if error_message:
            return (
                self._new_tb_with_expected()
                    .append_details(custom_details.OfTextRenderer(error_message))
                    .build_result(False)
            )

        return self._positive_matcher_application(model)

    def _positive_matcher_application(self, model: FileToCheck) -> MatchingResult:
        expected_file_path = self._file_path_for_file_with_expected_contents(model.tmp_file_space)
        actual_file_path = model.transformed_file_path()

        files_are_equal = self._do_compare(expected_file_path, actual_file_path)

        if files_are_equal:
            return (
                self._new_tb_with_expected()
                    .build_result(True)
            )
        else:
            diff_description = _file_diff_description(actual_file_path,
                                                      expected_file_path)
            return (
                self._new_tb_with_expected()
                    .append_details(
                    details.HeaderAndValue(
                        'Diff:',
                        details.PreFormattedString(_DiffString(diff_description), True)
                    )
                )
                    .build_result(False)
            )

    def _file_path_for_file_with_expected_contents(self, tmp_file_space: TmpDirFileSpace) -> pathlib.Path:
        if self._expected_contents.is_path:
            return self._expected_contents.path_value.primitive
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
                diff_description = _file_diff_description__old(actual_file_path,
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

    def _do_post_setup_validation__old(self) -> Optional[ErrorMessageResolver]:
        error_message = self._validator.validate_post_sds_if_applicable()
        return (
            None
            if error_message is None
            else env_dep_texts.as_old(env_dep_texts.constant_renderer(error_message))
        )

    def _new_tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._expected_detail_renderer)


def _validator_of_expected(expected_contents: StringOrPathDdv) -> DdvValidator:
    return expected_contents.validator__file_must_exist_as(FileType.REGULAR, True)


def _file_diff_description__old(actual_file_path: pathlib.Path,
                                expected_file_path: pathlib.Path) -> List[str]:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return list(diff)


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> Iterable[str]:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return diff


class _DiffString(StringConstructor):
    def __init__(self, lines: Iterable[str]):
        self._lines = lines

    def __str__(self) -> str:
        return '\n'.join(self._lines)


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

    def resolve(self) -> str:
        description_of_actual_file = self._checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE)
        failure_info_resolver = DiffFailureInfoResolver(
            description_of_actual_file,
            self._expectation_type,
            self._expected_value,
        )
        failure_info = failure_info_resolver.resolve(self._actual_info)
        return failure_info.error_message()
