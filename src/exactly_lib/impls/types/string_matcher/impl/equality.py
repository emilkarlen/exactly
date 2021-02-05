import difflib
import filecmp
import pathlib
from typing import Iterable, Sequence, Callable, Tuple, List

import exactly_lib.util.str_.read_lines
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.impls.types.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import PreOrPostSdsValidatorPrimitive
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv, StringSourceAdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_source import string_source
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.str_.str_constructor import StringConstructor
from exactly_lib.util.symbol_table import SymbolTable

_EXPECTED_STRING_HEADER = custom_details.EXPECTED + ' ' + syntax_elements.STRING_SYNTAX_ELEMENT.singular_name


def sdv(expected_contents: StringSourceSdv) -> StringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> MatcherDdv[StringSource]:
        expected_contents_ddv = expected_contents.resolve(symbols)

        return _EqualityStringMatcherDdv(expected_contents_ddv)

    return sdv_components.MatcherSdvFromParts(expected_contents.references, get_ddv)


class _EqualityStringMatcherDdv(MatcherDdv[StringSource]):
    def __init__(self, expected_contents: StringSourceDdv):
        super().__init__()
        self._expected_contents = expected_contents
        self._renderer_of_expected_value = details.Tree(expected_contents.structure())
        self._expected_detail_renderer = custom_details.expected(self._renderer_of_expected_value)

    def structure(self) -> StructureRenderer:
        return _EqualityStringMatcher.new_structure_tree(
            self._renderer_of_expected_value,
        )

    @property
    def validator(self) -> DdvValidator:
        return self._expected_contents.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return _EqualityStringMatcherAdv(
            self._expected_contents.value_of_any_dependency(tcds),
            ddv_validators.FixedPreOrPostSdsValidator(tcds, self.validator),
        )


class _EqualityStringMatcherAdv(MatcherAdv[StringSource]):
    def __init__(self,
                 expected_contents: StringSourceAdv,
                 validator: PreOrPostSdsValidatorPrimitive,
                 ):
        super().__init__()
        self._expected_contents = expected_contents
        self._validator = validator

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[StringSource]:
        return _EqualityStringMatcher(
            self._expected_contents.primitive(environment),
            self._validator,
        )


class _EqualityStringMatcher(StringMatcherImplBase):
    NAME = ' '.join((matcher_options.EQUALS_ARGUMENT,
                     syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.singular_name))

    @staticmethod
    def new_structure_tree(expected_contents: DetailsRenderer) -> StructureRenderer:
        return renderers.header_and_detail(
            _EqualityStringMatcher.NAME,
            expected_contents,
        )

    def __init__(self,
                 expected_contents: StringSource,
                 validator: PreOrPostSdsValidatorPrimitive,
                 ):
        super().__init__()
        self._expected_contents = expected_contents
        self._validator = validator
        self._expected_detail_renderer = custom_details.expected(
            details.Tree(expected_contents.structure())
        )
        result_of_match = self._new_tb_with_expected().build_result(True)
        self._applier = _ApplierWExtDepsCases(result_of_match,
                                              self._result_for_no_match,
                                              expected_contents)

    @property
    def name(self) -> str:
        return matcher_options.EQUALS_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return _EqualityStringMatcher.new_structure_tree(
            details.Tree(self._expected_contents.structure()),
        )

    def matches_w_trace(self, model: StringSource) -> MatchingResult:
        error_message = self._validator.validate_post_sds_if_applicable()
        if error_message:
            return (
                self._new_tb_with_expected()
                    .append_details(custom_details.OfTextRenderer(error_message))
                    .build_result(False)
            )

        return self._applier.match(model.contents())

    def _new_tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._expected_detail_renderer)

    def _result_for_no_match(self, actual: Sequence[DetailsRenderer]) -> MatchingResult:
        return (
            TraceBuilder(matcher_options.EQUALS_ARGUMENT)
                .append_details(self._expected_detail_renderer)
                .extend_details(actual)
                .build_result(False)
        )


class _ApplierWExtDepsCases:
    def __init__(self,
                 result_for_match: MatchingResult,
                 build_result_for_no_match: Callable[[Sequence[DetailsRenderer]], MatchingResult],
                 expected: StringSource,
                 ):
        self._build_result_for_no_match = build_result_for_no_match
        self._result_for_match = result_for_match
        self._expected = expected
        self._expected_unfrozen_has_ext_deps = expected.contents().may_depend_on_external_resources

    def match(self, actual: StringSourceContents) -> MatchingResult:
        self._expected.freeze()
        expt_deps__expected = self._expected.contents().may_depend_on_external_resources
        expt_deps__actual = actual.may_depend_on_external_resources

        if expt_deps__expected:
            if expt_deps__actual:
                handler = _ExtDepsOfBothHandler(self._result_for_match,
                                                self._build_result_for_no_match,
                                                self._expected.contents().as_file)
                return handler.match(actual)
            else:
                return self._ext_deps__only_expected(actual)
        else:
            if expt_deps__actual:
                return self._ext_deps__only_actual(actual)
            else:
                return self._ext_deps__none(actual)

    def _ext_deps__none(self, actual: StringSourceContents) -> MatchingResult:
        actual_str = actual.as_str
        expected = self._expected.contents().as_str

        values_are_equal = expected == actual_str

        if values_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match(
                self._details_for_ext_deps__non(expected, actual_str)
            )

    def _ext_deps__only_actual(self, actual: StringSourceContents) -> MatchingResult:
        expected = self._expected.contents().as_str
        actual_header, actual_may_be_longer = string_source.read_lines_as_str__w_minimum_num_chars(
            _min_num_chars_to_read(expected),
            actual,
        )
        contents_are_equal = expected == actual_header

        if contents_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match([
                custom_details.actual(
                    custom_details.string__maybe_longer(actual_header, actual_may_be_longer))
            ])

    def _ext_deps__only_expected(self, actual: StringSourceContents) -> MatchingResult:
        actual_str = actual.as_str

        expected_header, expected_may_be_longer = self._read_expected_header(_min_num_chars_to_read(actual_str))

        values_are_equal = expected_header == actual_str

        if values_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match([
                custom_details.expected__custom(
                    _EXPECTED_STRING_HEADER,
                    custom_details.string__maybe_longer(expected_header, expected_may_be_longer)
                ),
                custom_details.actual(
                    custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(actual_str)
                )
            ])

    def _details_for_ext_deps__non(self, expected: str, actual: str) -> Sequence[DetailsRenderer]:
        ret_val = []
        if self._expected_unfrozen_has_ext_deps:
            ret_val.append(
                custom_details.expected__custom(
                    _EXPECTED_STRING_HEADER,
                    custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(expected)
                )
            )
        ret_val.append(
            custom_details.actual(
                custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(actual))
        )
        return ret_val

    def _read_expected_header(self, min_num_chars: int) -> Tuple[str, bool]:
        with self._expected.contents().as_file.open() as lines:
            return exactly_lib.util.str_.read_lines.read_lines_as_str__w_minimum_num_chars(
                min_num_chars,
                lines,
            )


class _ExtDepsOfBothHandler:
    def __init__(self,
                 result_for_match: MatchingResult,
                 build_result_for_no_match: Callable[[Sequence[DetailsRenderer]], MatchingResult],
                 expected: pathlib.Path,
                 ):
        self._result_for_match = result_for_match
        self._build_result_for_no_match = build_result_for_no_match
        self._expected = expected

    def match(self, actual: StringSourceContents) -> MatchingResult:
        actual_file_path = actual.as_file

        files_are_equal = self._do_compare(actual_file_path)

        if files_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match([
                self._actual_file_contents_detail(actual_file_path),
                self._diff_detail(actual_file_path),
            ])

    def _read_expected_header(self, min_num_chars: int) -> Tuple[str, bool]:
        with self._expected.open() as lines:
            return exactly_lib.util.str_.read_lines.read_lines_as_str__w_minimum_num_chars(
                min_num_chars,
                lines,
            )

    def _do_compare(self,
                    processed_actual_file_path: pathlib.Path) -> bool:
        actual_file_name = str(processed_actual_file_path)
        expected_file_name = str(self._expected)
        return filecmp.cmp(actual_file_name, expected_file_name, shallow=False)

    @staticmethod
    def _actual_file_contents_detail(actual: pathlib.Path) -> DetailsRenderer:
        with actual.open() as f:
            contents = f.read(custom_details.STRING__DEFAULT_DISPLAY_LEN + 1)

        return custom_details.actual(
            custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(contents)
        )

    def _diff_detail(self, actual: pathlib.Path) -> DetailsRenderer:
        diff_description = _file_diff_description(actual,
                                                  self._expected)
        return custom_details.diff(
            details.PreFormattedString(
                _DiffString(diff_description), True)
        )


def _min_num_chars_to_read(operand: str) -> int:
    return len(operand) + 1 + custom_details.STRING__EXTRA_TO_READ_FOR_ERROR_MESSAGES


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> Iterable[str]:
    expected_lines = _lines_of(expected_file_path)
    actual_lines = _lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile=custom_details.EXPECTED,
                                tofile=custom_details.ACTUAL)
    return diff


class _DiffString(StringConstructor):
    def __init__(self, lines: Iterable[str]):
        self._lines = lines

    def __str__(self) -> str:
        return ''.join(self._lines)


def _lines_of(file_path: pathlib.Path) -> List[str]:
    with file_path.open() as f:
        ret_val = list(f.readlines())

    if ret_val:
        ret_val[-1] = _with_nl_ending(ret_val[-1])

    return ret_val


def _with_nl_ending(s: str) -> str:
    return (
        s + '\n'
        if s == '' or s[-1] != '\n'
        else
        s
    )
