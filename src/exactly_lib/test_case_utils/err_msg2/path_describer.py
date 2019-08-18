from abc import ABC, abstractmethod

from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathDescriberForResolver(ABC):
    @property
    @abstractmethod
    def resolver(self) -> Renderer[str]:
        pass


class PathDescriberForValue(PathDescriberForResolver):
    @property
    @abstractmethod
    def value(self) -> Renderer[str]:
        pass


class PathDescriberForPrimitive(PathDescriberForValue):
    @property
    @abstractmethod
    def primitive(self) -> Renderer[str]:
        pass
