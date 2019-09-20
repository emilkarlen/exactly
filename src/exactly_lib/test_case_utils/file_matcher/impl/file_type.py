import pathlib
from typing import Optional

from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel


class FileMatcherType(FileMatcher):
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
    def option_description(self) -> str:
        return 'type is ' + file_properties.TYPE_INFO[self._file_type].description

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
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
