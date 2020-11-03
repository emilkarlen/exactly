from typing import Optional, Set

from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.string_or_path.primitive import SourceType, StringOrPath
from exactly_lib.symbol.value_type import DataValueType
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.string.string_ddv import StringDdv


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

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringOrPath:
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
        from exactly_lib.impls.types.path.path_check import PathCheckDdv, PathCheckDdvValidator
        from exactly_lib.impls.file_properties import must_exist_as
        frc = PathCheckDdv(self._path,
                           must_exist_as(file_type, follow_symlinks))
        return PathCheckDdvValidator(frc)
