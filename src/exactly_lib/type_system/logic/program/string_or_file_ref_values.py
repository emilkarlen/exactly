import pathlib
from typing import Optional, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.value_type import DataValueType


class StringOrPath(tuple):
    """
    Either a :class:`str` or a :class:`pathlib.Path`
    """

    def __new__(cls,
                string_value: Optional[str],
                file_value: Optional[pathlib.Path]):
        return tuple.__new__(cls, (DataValueType.STRING if string_value is not None else DataValueType.PATH,
                                   string_value,
                                   file_value))

    @property
    def value_type(self) -> DataValueType:
        """
        :return: Either STRING or PATH
        """
        return self[0]

    @property
    def is_path(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is a string accessed via `string_value`
        """
        return self.value_type is DataValueType.PATH

    @property
    def string_value(self) -> str:
        """
        :return: Not None iff :class:`DataValueType` is NOT `DataValueType.STRING`
        """
        return self[1]

    @property
    def file_ref_value(self) -> pathlib.Path:
        """
        :return: Not None iff :class:`DataValueType` is `DataValueType.PATH`
        """
        return self[2]


class StringOrFileRefValue(MultiDirDependentValue[StringOrPath]):
    """
    Either a :class:`StringValue` or a :class:`FileRef`
    """

    def __init__(self,
                 string_value: Optional[StringValue],
                 file_value: Optional[FileRef]):
        self._value_type = DataValueType.STRING if string_value is not None else DataValueType.PATH
        self._string_value = string_value
        self._file_ref_value = file_value

    @property
    def value_type(self) -> DataValueType:
        """
        :return: Either STRING or PATH
        """
        return self._value_type

    @property
    def is_file_ref(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is a string accessed via `string_value`
        """
        return self.value_type is DataValueType.PATH

    @property
    def string_value(self) -> StringValue:
        """
        :return: Not None iff :class:`DataValueType` is NOT `DataValueType.STRING`
        """
        return self._string_value

    @property
    def file_ref_value(self) -> FileRef:
        """
        :return: Not None iff :class:`DataValueType` is `DataValueType.PATH`
        """
        return self._file_ref_value

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        if self.is_file_ref:
            return self.file_ref_value.resolving_dependencies()
        else:
            return self.string_value.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> StringOrPath:
        if self.is_file_ref:
            return StringOrPath(None, self._file_ref_value.value_when_no_dir_dependencies())
        else:
            return StringOrPath(self._string_value.value_when_no_dir_dependencies(), None)

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringOrPath:
        if self.is_file_ref:
            return StringOrPath(None, self._file_ref_value.value_of_any_dependency(home_and_sds))
        else:
            return StringOrPath(self._string_value.value_of_any_dependency(home_and_sds), None)


def of_string(string_value: StringValue) -> StringOrFileRefValue:
    return StringOrFileRefValue(string_value, None)


def of_file_ref(file_ref: FileRef) -> StringOrFileRefValue:
    return StringOrFileRefValue(None, file_ref)
