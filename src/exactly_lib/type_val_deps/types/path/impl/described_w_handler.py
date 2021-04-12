from abc import ABC, abstractmethod
from pathlib import Path

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.path_describer import PathDescriberForDdv, \
    PathDescriberForPrimitive


class PathDescriberHandlerForPrimitive(ABC):
    @property
    @abstractmethod
    def describer(self) -> PathDescriberForPrimitive:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def child(self,
              child_path: Path,
              child_path_component: str) -> 'PathDescriberHandlerForPrimitive':
        raise NotImplementedError('abstract method')

    @abstractmethod
    def parent(self, parent_path: Path) -> 'PathDescriberHandlerForPrimitive':
        raise NotImplementedError('abstract method')


class PathDescriberHandlerForDdv(ABC):
    @property
    @abstractmethod
    def describer(self) -> PathDescriberForDdv:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def value_when_no_dir_dependencies(self, primitive: Path) -> PathDescriberHandlerForPrimitive:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def value_pre_sds(self, primitive: Path, hds: HomeDs) -> PathDescriberHandlerForPrimitive:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def value_post_sds__wo_hds(self, primitive: Path,
                               sds: SandboxDs) -> PathDescriberHandlerForPrimitive:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def value_post_sds(self, primitive: Path, tcds: TestCaseDs) -> PathDescriberHandlerForPrimitive:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def value_of_any_dependency(self, primitive: Path, tcds: TestCaseDs) -> PathDescriberHandlerForPrimitive:
        raise NotImplementedError('abstract method')


class DescribedPathWHandler(DescribedPath):
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

    def child(self, child_path_component: str) -> DescribedPath:
        child_path = self._path / child_path_component
        return DescribedPathWHandler(
            child_path,
            self._describer_handler.child(child_path, child_path_component)
        )

    def parent(self) -> DescribedPath:
        parent_path = self._path.parent
        return DescribedPathWHandler(
            parent_path,
            self._describer_handler.parent(parent_path)
        )
