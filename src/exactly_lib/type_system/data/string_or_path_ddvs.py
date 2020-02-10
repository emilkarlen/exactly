import enum
from typing import Optional, Set

from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.data.path_ddv import DescribedPath, PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.value_type import DataValueType


class SourceType(enum.Enum):
    STRING = 1
    HERE_DOC = 2
    PATH = 3


class StringOrPath(tuple):
    """
    Either a :class:`str` or a :class:`pathlib.Path`
    """

    def __new__(cls,
                source_type: SourceType,
                string_value: Optional[str],
                file_value: Optional[DescribedPath]):
        return tuple.__new__(cls, (DataValueType.STRING if string_value is not None else DataValueType.PATH,
                                   string_value,
                                   file_value,
                                   source_type))

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
    def path_value(self) -> DescribedPath:
        """
        :return: Not None iff :class:`DataValueType` is `DataValueType.PATH`
        """
        return self[2]

    @property
    def source_type(self) -> SourceType:
        return self[3]


class StringOrPathDdv(MultiDependenciesDdv[StringOrPath]):
    """
    Either a :class:`StringValue` or a :class:`PathDdv`
    """

    def __init__(self,
                 source_type: SourceType,
                 string: Optional[StringDdv],
                 path: Optional[PathDdv]):
        self._source_type = source_type
        self._type = DataValueType.STRING if string is not None else DataValueType.PATH
        self._string = string
        self._path = path

    @property
    def source_type(self) -> SourceType:
        return self._source_type

    @property
    def value_type(self) -> DataValueType:
        """
        :return: Either STRING or PATH
        """
        return self._type

    @property
    def is_path(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is a string accessed via `string_value`
        """
        return self.value_type is DataValueType.PATH

    @property
    def string(self) -> StringDdv:
        """
        :return: Not None iff :class:`DataValueType` is NOT `DataValueType.STRING`
        """
        return self._string

    @property
    def path(self) -> PathDdv:
        """
        :return: Not None iff :class:`DataValueType` is NOT `DataValueType.PATH`
        """
        return self._path

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        if self.is_path:
            return self._path.resolving_dependencies()
        else:
            return self.string.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> StringOrPath:
        if self.is_path:
            return StringOrPath(self._source_type,
                                None,
                                self._path.value_when_no_dir_dependencies__d())
        else:
            return StringOrPath(self._source_type,
                                self._string.value_when_no_dir_dependencies(),
                                None)

    def value_of_any_dependency(self, tcds: Tcds) -> StringOrPath:
        if self.is_path:
            return StringOrPath(self._source_type,
                                None,
                                self._path.value_of_any_dependency__d(tcds))
        else:
            return StringOrPath(self._source_type,
                                self._string.value_of_any_dependency(tcds),
                                None)

    def validator__file_must_exist_as(self,
                                      file_type: FileType,
                                      follow_symlinks: bool = True
                                      ) -> DdvValidator:
        if not self.is_path:
            return ddv_validation.ConstantDdvValidator.new_success()
        from exactly_lib.test_case_utils.path_check import PathCheckDdv, PathCheckDdvValidator
        from exactly_lib.test_case_utils.file_properties import must_exist_as
        frc = PathCheckDdv(self._path,
                           must_exist_as(file_type, follow_symlinks))
        return PathCheckDdvValidator(frc)
