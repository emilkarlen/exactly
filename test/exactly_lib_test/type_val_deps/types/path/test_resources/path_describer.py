from pathlib import Path
from typing import Optional

from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.type_val_deps.types.path.impl.described_w_handler import PathDescriberHandlerForPrimitive
from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive
from exactly_lib.util.render.combinators import ConstantR
from exactly_lib.util.render.renderer import Renderer


class PathDescriberForPrimitiveTestImpl(PathDescriberForPrimitive):
    def __init__(self, rendition: str = 'described path'):
        self._rendition = rendition

    @property
    def primitive(self) -> Renderer[str]:
        return ConstantR('primitive: ' + self._rendition)

    @property
    def value(self) -> Renderer[str]:
        return ConstantR('value: ' + self._rendition)

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return None


class PathDescriberHandlerForPrimitiveTestImpl(PathDescriberHandlerForPrimitive):
    def __init__(self, rendition: str = 'described path'):
        self._rendition = rendition

    @property
    def describer(self) -> PathDescriberForPrimitive:
        return PathDescriberForPrimitiveTestImpl(self._rendition)

    def child(self, child_path: Path, child_path_component: str) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveTestImpl(
            str(child_path)
        )

    def parent(self, parent_path: Path) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveTestImpl(
            str(parent_path)
        )
