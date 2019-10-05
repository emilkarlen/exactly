import pathlib
from typing import Optional

from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.description_tree import details
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.trace.impls.trace_building import TraceBuilder


class FileMatcherType(FileMatcherImplBase):
    """Matches the type of file."""

    def __init__(self, file_type: file_properties.FileType):
        self._file_type = file_type
        self._path_predicate = file_properties.TYPE_INFO[self._file_type].pathlib_path_predicate
        self._stat_method = (pathlib.Path.lstat
                             if file_type is file_properties.FileType.SYMLINK
                             else pathlib.Path.stat)

    @property
    def file_type(self) -> file_properties.FileType:
        return self._file_type

    @property
    def name(self) -> str:
        return file_matcher.TYPE_MATCHER_NAME

    @property
    def option_description(self) -> str:
        return 'type is ' + file_properties.TYPE_INFO[self._file_type].description

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        path = model.path.primitive
        try:
            stat_result = self._stat_method(path)
        except OSError as ex:
            return err_msg_resolvers.sequence_of_parts([
                err_msg_resolvers.of_path(model.path.describer),
                err_msg_resolvers.constant(str(ex))
            ])
        file_type = file_properties.lookup_file_type(stat_result)
        if file_type is self._file_type:
            return None
        else:
            return err_msg_resolvers.sequence_of_parts([
                err_msg_resolvers.of_path(model.path.describer),
                _FileTypeErrorMessageResolver(file_type)
            ])

    def matches(self, model: FileMatcherModel) -> bool:
        return self._path_predicate(model.path.primitive)

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

    def _result_for_exception(self, path: DescribedPathPrimitive, ex: Exception) -> MatchingResult:
        tb = (
            self.__tb_with_expected()
                .append_details(details.HeaderAndValue(types.PATH_TYPE_INFO.singular_name.capitalize(),
                                                       details.PathValueDetailsRenderer(path.describer)))
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
            details.actual(
                details.String(actual_type_description)
            )
        )
        return tb.build_result(False)

    def __tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(
            details.expected(
                details.String(
                    file_properties.TYPE_INFO[self._file_type].description)
            )
        )


class _FileTypeErrorMessageResolver(ErrorMessageResolver):
    def __init__(self, actual_file_type: Optional[file_properties.FileType]):
        self._actual_file_type = actual_file_type

    def resolve(self) -> str:
        actual_type_description = (
            'unknown'
            if self._actual_file_type is None
            else self._actual_file_type.name
        )
        return 'Actual file type is ' + actual_type_description
