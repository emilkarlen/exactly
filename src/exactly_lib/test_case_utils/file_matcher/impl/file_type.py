from exactly_lib.test_case_utils import file_properties
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel


class FileMatcherType(FileMatcher):
    """Matches the type of file."""

    def __init__(self, file_type: file_properties.FileType):
        self._file_type = file_type
        self._path_predicate = file_properties.TYPE_INFO[self._file_type].pathlib_path_predicate

    @property
    def file_type(self) -> file_properties.FileType:
        return self._file_type

    @property
    def option_description(self) -> str:
        return 'type is ' + file_properties.TYPE_INFO[self._file_type].description

    def matches(self, model: FileMatcherModel) -> bool:
        return self._path_predicate(model.path)
