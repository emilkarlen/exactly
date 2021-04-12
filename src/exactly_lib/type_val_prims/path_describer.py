from abc import abstractmethod
from typing import Optional

from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.util.render.renderer import Renderer


class PathDescriberForDdv:
    @property
    @abstractmethod
    def value(self) -> Renderer[str]:
        raise NotImplementedError('abstract method')

    @property
    @abstractmethod
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        """
        :return: None iff path is absolute
        """
        raise NotImplementedError('abstract method')


class PathDescriberForPrimitive(PathDescriberForDdv):
    @property
    @abstractmethod
    def primitive(self) -> Renderer[str]:
        raise NotImplementedError('abstract method')
