import difflib
import filecmp
import pathlib
from typing import Iterable

from exactly_lib.symbol.data.string_or_path import StringOrPathSdv
from exactly_lib.symbol.sdv_validation import PreOrPostSdsValidatorPrimitive
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_system.data.string_or_path_ddvs import StringOrPathDdv, StringOrPath
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherAdv, MatcherDdv, MODEL, MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcherDdv, FileToCheck, StringMatcher, \
    StringMatcherSdv
from exactly_lib.util import file_utils
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.file_utils import TmpDirFileSpace, tmp_text_file_containing
from exactly_lib.util.strings import StringConstructor
from exactly_lib.util.symbol_table import SymbolTable


def sdv(expected_contents: StringOrPathSdv) -> StringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> MatcherDdv[FileToCheck]:
        expected_contents_ddv = expected_contents.resolve(symbols)

        return ddv(expected_contents_ddv)

    return sdv_components.MatcherSdvFromParts(expected_contents.references, get_ddv)


def ddv(expected_contents: StringOrPathDdv) -> StringMatcherDdv:
    return EqualityStringMatcherDdv(
        expected_contents,
        _validator_of_expected(expected_contents),
    )


class EqualityStringMatcherAdv(MatcherAdv[FileToCheck]):
    def __init__(self,
                 expected_contents: StringOrPath,
                 validator: PreOrPostSdsValidatorPrimitive,
                 ):
        super().__init__()
        self._expected_contents = expected_contents
        self._validator = validator

    def primitive(self, environment: ApplicationEnvironment) -> StringMatcher:
        return EqualityStringMatcher(
            self._expected_contents,
            self._validator,
            environment.tmp_files_space,
        )


class EqualityStringMatcherDdv(MatcherDdv[FileToCheck]):
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

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return EqualityStringMatcherAdv(
            self._expected_contents.value_of_any_dependency(tcds),
            ddv_validators.FixedPreOrPostSdsValidator(tcds, self._validator),
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
                 tmp_file_space: TmpDirFileSpace,
                 ):
        super().__init__()
        self._expected_contents = expected_contents
        self._validator = validator
        self._renderer_of_expected_value = custom_details.StringOrPath(expected_contents)
        self._expected_detail_renderer = custom_details.expected(self._renderer_of_expected_value)
        self._tmp_file_space = tmp_file_space

    @property
    def name(self) -> str:
        return matcher_options.EQUALS_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return EqualityStringMatcher.new_structure_tree(
            custom_details.StringOrPath(self._expected_contents),
        )

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        error_message = self._validator.validate_post_sds_if_applicable()
        if error_message:
            return (
                self._new_tb_with_expected()
                    .append_details(custom_details.OfTextRenderer(error_message))
                    .build_result(False)
            )

        return self._positive_matcher_application(model)

    def _positive_matcher_application(self, model: FileToCheck) -> MatchingResult:
        expected_file_path = self._file_path_for_file_with_expected_contents(self._tmp_file_space)
        actual_file_path = model.transformed_file_path(self._tmp_file_space)

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

    def _new_tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._expected_detail_renderer)


def _validator_of_expected(expected_contents: StringOrPathDdv) -> DdvValidator:
    return expected_contents.validator__file_must_exist_as(FileType.REGULAR, True)


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
