from abc import ABC, abstractmethod
from pathlib import Path

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data.file_ref import DescribedPathPrimitive
from exactly_lib.type_system.data.path_describer import PathDescriberForValue, \
    PathDescriberForPrimitive


class PathDescriberHandlerForPrimitive(ABC):
    @property
    @abstractmethod
    def describer(self) -> PathDescriberForPrimitive:
        pass

    @abstractmethod
    def child(self,
              child_path: Path,
              child_path_component: str) -> 'PathDescriberHandlerForPrimitive':
        pass

    @abstractmethod
    def parent(self, parent_path: Path) -> 'PathDescriberHandlerForPrimitive':
        pass


class PathDescriberHandlerForValue(ABC):
    @property
    @abstractmethod
    def describer(self) -> PathDescriberForValue:
        pass

    @abstractmethod
    def value_when_no_dir_dependencies(self, primitive: Path) -> PathDescriberHandlerForPrimitive:
        pass

    @abstractmethod
    def value_pre_sds(self, primitive: Path, hds: HomeDirectoryStructure) -> PathDescriberHandlerForPrimitive:
        pass

    @abstractmethod
    def value_post_sds__wo_hds(self, primitive: Path,
                               sds: SandboxDirectoryStructure) -> PathDescriberHandlerForPrimitive:
        pass

    @abstractmethod
    def value_post_sds(self, primitive: Path, tcds: HomeAndSds) -> PathDescriberHandlerForPrimitive:
        pass

    @abstractmethod
    def value_of_any_dependency(self, primitive: Path, tcds: HomeAndSds) -> PathDescriberHandlerForPrimitive:
        pass


class DescribedPathPrimitiveWHandler(DescribedPathPrimitive):
    def __init__(self,
                 path: Path,
                 describer_handler: PathDescriberHandlerForPrimitive,
                 ):
        self._path = path
        self._describer_handler = describer_handler

    @property
    def primitive(self) -> Path:
        return self._path

    @property
    def describer(self) -> PathDescriberForPrimitive:
        return self._describer_handler.describer

    def child(self, child_path_component: str) -> DescribedPathPrimitive:
        child_path = self._path / child_path_component
        return DescribedPathPrimitiveWHandler(
            child_path,
            self._describer_handler.child(child_path, child_path_component)
        )

    def parent(self) -> DescribedPathPrimitive:
        parent_path = self._path.parent
        return DescribedPathPrimitiveWHandler(
            parent_path,
            self._describer_handler.parent(parent_path)
        )