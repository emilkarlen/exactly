from typing import Optional, Callable

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.path_describer import PathDescriberForDdv, \
    PathDescriberForPrimitive
from exactly_lib.util.render.renderer import Renderer


class PathDescriberForDdvFromStr(PathDescriberForDdv):
    def __init__(self,
                 value: Renderer[str],
                 relativity: Callable[[], Optional[DirectoryStructurePartition]]
                 ):
        self._value = value
        self._relativity = relativity

    @property
    def value(self) -> Renderer[str]:
        return self._value

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._relativity()


class PathDescriberForPrimitiveFromStr(PathDescriberForPrimitive):
    def __init__(self,
                 value: PathDescriberForDdv,
                 primitive: Renderer[str],
                 ):
        self._value = value
        self._primitive = primitive

    @property
    def value(self) -> Renderer[str]:
        return self._value.value

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._value.resolving_dependency

    @property
    def primitive(self) -> Renderer[str]:
        return self._primitive
