from typing import Optional, Callable

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.path_describer import PathDescriberForResolver, PathDescriberForValue, \
    PathDescriberForPrimitive
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathDescriberForResolverFromStr(PathDescriberForResolver):
    def __init__(self,
                 resolver: Renderer[str],
                 ):
        self._resolver = resolver

    @property
    def resolver(self) -> Renderer[str]:
        return self._resolver


class PathDescriberForValueFromStr(PathDescriberForValue):
    def __init__(self,
                 resolver: Renderer[str],
                 value: Renderer[str],
                 relativity: Callable[[], Optional[DirectoryStructurePartition]]
                 ):
        self._resolver = resolver
        self._value = value
        self._relativity = relativity

    @property
    def resolver(self) -> Renderer[str]:
        return self._resolver

    @property
    def value(self) -> Renderer[str]:
        return self._value

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._relativity()


class PathDescriberForPrimitiveFromStr(PathDescriberForPrimitive):
    def __init__(self,
                 value: PathDescriberForValue,
                 primitive: Renderer[str],
                 ):
        self._value = value
        self._primitive = primitive

    @property
    def resolver(self) -> Renderer[str]:
        return self._value.resolver

    @property
    def value(self) -> Renderer[str]:
        return self._value.value

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._value.resolving_dependency

    @property
    def primitive(self) -> Renderer[str]:
        return self._primitive
