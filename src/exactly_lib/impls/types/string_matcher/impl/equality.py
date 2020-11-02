import difflib
import filecmp
import pathlib
from typing import Iterable, Sequence, Callable, Tuple

import exactly_lib.util.str_.read_lines
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.impls.types.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import PreOrPostSdsValidatorPrimitive
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_deps.types.string_or_path.string_or_path_ddvs import StringOrPathDdv, StringOrPath
from exactly_lib.type_val_deps.types.string_or_path.string_or_path_sdv import StringOrPathSdv
from exactly_lib.type_val_prims import string_model
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.file_utils import misc_utils
from exactly_lib.util.str_.str_constructor import StringConstructor
from exactly_lib.util.symbol_table import SymbolTable


def sdv(expected_contents: StringOrPathSdv) -> StringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> MatcherDdv[StringModel]:
        expected_contents_ddv = expected_contents.resolve(symbols)

        return EqualityStringMatcherDdv(
            expected_contents_ddv,
            _validator_of_expected(expected_contents_ddv),
        )

    return sdv_components.MatcherSdvFromParts(expected_contents.references, get_ddv)


class EqualityStringMatcherDdv(MatcherDdv[StringModel]):
    def __init__(self,
                 expected_contents: StringOrPathDdv,
                 validator: DdvValidator,
                 ):
        super().__init__()
        self._expected_contents = expected_contents
        self._validator = validator
        self._renderer_of_expected_value = custom_details.StringOrPath(expected_contents)
        self._expected_detail_renderer = custom_details.expected(self._renderer_of_expected_value)

    def structure(self) -> StructureRenderer:
        return EqualityStringMatcher.new_structure_tree(
            custom_details.StringOrPathDdv(self._expected_contents),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            EqualityStringMatcher(
                self._expected_contents.value_of_any_dependency(tcds),
                ddv_validators.FixedPreOrPostSdsValidator(tcds, self._validator),
            )
        )


class EqualityStringMatcher(StringMatcherImplBase):
    NAME = matcher_options.EQUALS_ARGUMENT

    @staticmethod
    def new_structure_tree(expected_contents: DetailsRenderer) -> StructureRenderer:
        return renderers.header_and_detail(
            EqualityStringMatcher.NAME,
            expected_contents,
        )

    def __init__(self,
                 expected_contents: StringOrPath,
                 validator: PreOrPostSdsValidatorPrimitive,
                 ):
        super().__init__()
        self._expected_contents = expected_contents
        self._validator = validator
        self._expected_detail_renderer = custom_details.expected(
            custom_details.StringOrPath(expected_contents)
        )
        result_of_match = self._new_tb_with_expected().build_result(True)
        self._applier = (
            _ApplierForExpectedOfPath(result_of_match,
                                      self._result_for_no_match,
                                      expected_contents.path_value.primitive)
            if expected_contents.is_path
            else
            _ApplierForExpectedOfString(result_of_match,
                                        self._result_for_no_match,
                                        expected_contents.string_value)
        )

    @property
    def name(self) -> str:
        return matcher_options.EQUALS_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return EqualityStringMatcher.new_structure_tree(
            custom_details.StringOrPath(self._expected_contents),
        )

    def matches_w_trace(self, model: StringModel) -> MatchingResult:
        error_message = self._validator.validate_post_sds_if_applicable()
        if error_message:
            return (
                self._new_tb_with_expected()
                    .append_details(custom_details.OfTextRenderer(error_message))
                    .build_result(False)
            )

        return self._applier.match(model)

    def _new_tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._expected_detail_renderer)

    def _result_for_no_match(self, actual: Sequence[DetailsRenderer]) -> MatchingResult:
        return (
            TraceBuilder(matcher_options.EQUALS_ARGUMENT)
                .append_details(self._expected_detail_renderer)
                .extend_details(actual)
                .build_result(False)
        )


class _Applier:
    def match(self, model: StringModel) -> MatchingResult:
        return (
            self._ext_deps(model)
            if model.may_depend_on_external_resources
            else
            self._no_ext_deps(model)
        )

    def _no_ext_deps(self, model: StringModel) -> MatchingResult:
        raise NotImplementedError('abstract method')

    def _ext_deps(self, model: StringModel) -> MatchingResult:
        raise NotImplementedError('abstract method')


class _ApplierForExpectedOfString(_Applier):
    def __init__(self,
                 result_for_match: MatchingResult,
                 build_result_for_no_match: Callable[[Sequence[DetailsRenderer]], MatchingResult],
                 expected: str,
                 ):
        self._build_result_for_no_match = build_result_for_no_match
        self._result_for_match = result_for_match
        self._expected = expected

    def _no_ext_deps(self, model: StringModel) -> MatchingResult:
        actual = model.as_str
        files_are_equal = self._expected == actual

        if files_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match([
                custom_details.actual(
                    custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(actual))
            ])

    def _ext_deps(self, model: StringModel) -> MatchingResult:
        actual_header, actual_may_be_longer = string_model.read_lines_as_str__w_minimum_num_chars(
            _min_num_chars_to_read(self._expected),
            model,
        )
        files_are_equal = self._expected == actual_header

        if files_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match([
                custom_details.actual(
                    custom_details.string__maybe_longer(actual_header, actual_may_be_longer))
            ])


class _ApplierForExpectedOfPath(_Applier):
    def __init__(self,
                 result_for_match: MatchingResult,
                 build_result_for_no_match: Callable[[Sequence[DetailsRenderer]], MatchingResult],
                 expected: pathlib.Path,
                 ):
        self._result_for_match = result_for_match
        self._build_result_for_no_match = build_result_for_no_match
        self._expected = expected

    def _no_ext_deps(self, model: StringModel) -> MatchingResult:
        actual = model.as_str

        expected_header, expected_may_be_longer = self._read_expected_header(_min_num_chars_to_read(actual))

        files_are_equal = expected_header == actual

        if files_are_equal:
            return self._result_for_match
        else:
            return self._build_result_for_no_match([
                custom_details.actual(
                    custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(actual))
            ])

    def _ext_deps(self, model: StringModel) -> MatchingResult:
        actual_file_path = model.as_file

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


def _validator_of_expected(expected_contents: StringOrPathDdv) -> DdvValidator:
    return expected_contents.validator__file_must_exist_as(FileType.REGULAR, True)


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> Iterable[str]:
    expected_lines = misc_utils.lines_of(expected_file_path)
    actual_lines = misc_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return diff


class _DiffString(StringConstructor):
    def __init__(self, lines: Iterable[str]):
        self._lines = lines

    def __str__(self) -> str:
        return ''.join(self._lines)
