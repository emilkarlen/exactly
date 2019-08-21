from pathlib import Path
from typing import Optional

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl.described_path_w_handler import PathDescriberHandlerForPrimitive
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.rendering.renderer_combinators import ConstantR


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
    def resolver(self) -> Renderer[str]:
        return ConstantR('resolver: ' + self._rendition)

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
