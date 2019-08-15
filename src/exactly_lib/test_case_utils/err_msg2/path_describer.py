from abc import ABC, abstractmethod

from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import LineElement


class PathDescriberForResolver(ABC):
    @property
    @abstractmethod
    def resolver(self) -> Renderer[LineElement]:
        pass


class PathDescriberForValue(PathDescriberForResolver):
    @property
    @abstractmethod
    def value(self) -> Renderer[LineElement]:
        pass


class PathDescriberForPrimitive(PathDescriberForValue):
    @property
    @abstractmethod
    def primitive(self) -> Renderer[LineElement]:
        pass
