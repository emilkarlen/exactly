import pathlib
from typing import Optional

from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import details


class FileMatcherType(MatcherImplBase[FileMatcherModel]):
    """Matches the type of file."""

    def __init__(self, file_type: file_properties.FileType):
        super().__init__()
        self._file_type = file_type
        self._stat_method = (pathlib.Path.lstat
                             if file_type is file_properties.FileType.SYMLINK
                             else pathlib.Path.stat)
        self._renderer_of_expected_value = details.String(
            file_properties.TYPE_INFO[self._file_type].description)

        self._renderer_of_expected = custom_details.expected(self._renderer_of_expected_value)

    @property
    def file_type(self) -> file_properties.FileType:
        return self._file_type

    @property
    def name(self) -> str:
        return file_matcher.TYPE_MATCHER_NAME

    def _structure(self) -> StructureRenderer:
        return (
            self._new_structure_builder()
                .append_details(self._renderer_of_expected_value)
                .as_render()
        )

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        path = model.path.primitive
        try:
            stat_result = self._stat_method(path)
        except OSError as ex:
            return self._result_for_exception(model.path, ex)
        actual_file_type = file_properties.lookup_file_type(stat_result)
        if actual_file_type is self._file_type:
            return self.__tb_with_expected().build_result(True)
        else:
            return self._result_for_unexpected(actual_file_type)

    def _result_for_exception(self, path: DescribedPath, ex: Exception) -> MatchingResult:
        tb = (
            self.__tb_with_expected()
                .append_details(details.HeaderAndValue(types.PATH_TYPE_INFO.singular_name.capitalize(),
                                                       custom_details.PathDdvDetailsRenderer(path.describer)))
                .append_details(details.HeaderAndValue('Error',
                                                       details.String(ex)))

        )
        return tb.build_result(False)

    def _result_for_unexpected(self,
                               actual: Optional[file_properties.FileType]) -> MatchingResult:
        actual_type_description = (
            'unknown'
            if actual is None
            else file_properties.TYPE_INFO[actual].description
        )
        tb = self.__tb_with_expected().append_details(
            custom_details.actual(
                details.String(actual_type_description)
            )
        )
        return tb.build_result(False)

    def __tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._renderer_of_expected)
