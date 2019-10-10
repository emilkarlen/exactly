from abc import abstractmethod
from typing import Optional

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathDescriberForValue:
    @property
    @abstractmethod
    def value(self) -> Renderer[str]:
        pass

    @property
    @abstractmethod
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        """
        :return: None iff path is absolute
        """
        pass


class PathDescriberForPrimitive(PathDescriberForValue):
    @property
    @abstractmethod
    def primitive(self) -> Renderer[str]:
        pass
