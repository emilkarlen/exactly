from abc import ABC, abstractmethod
from typing import Optional, Sequence, List

from exactly_lib.impls.text_render import header_rendering
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive, PathDescriberForDdv
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, ElementProperties
from exactly_lib.util.str_.str_constructor import ToStringObject


class PathRepresentationsRenderers(ABC):
    """Gives renderers for each path representation that should be displayed"""

    @abstractmethod
    def renders(self) -> List[Renderer[str]]:
        raise NotImplementedError('abstract method')


class PathRepresentationsRenderersForDdv(PathRepresentationsRenderers):
    def __init__(self, path: PathDescriberForDdv):
        self._path = path

    def renders(self) -> List[Renderer[str]]:
        return [self._path.value]


class PathRepresentationsRenderersForPrimitive(PathRepresentationsRenderers):
    """Renders DDV, and optional primitive if is rel HDS"""

    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def renders(self) -> List[Renderer[str]]:
        p = self._path
        return (
            [p.value, p.primitive]
            if p.resolving_dependency is DirectoryStructurePartition.HDS
            else
            [p.value]
        )


class PathMinorBlock(Renderer[MinorBlock]):
    def __init__(self,
                 path: PathRepresentationsRenderers,
                 element_properties: ElementProperties = text_struct.ELEMENT_PROPERTIES__INDENTED
                 ):
        self._path = path
        self._element_properties = element_properties

    def render(self) -> MinorBlock:
        return MinorBlock([
            text_struct.LineElement(
                text_struct.StringLineObject(line.render())
            )
            for line in self._path.renders()
        ],
            self._element_properties,
        )


def minor_block_renderer_of_primitive(path: PathDescriberForPrimitive) -> Renderer[MinorBlock]:
    return PathMinorBlock(
        PathRepresentationsRenderersForPrimitive(path),
        text_struct.ELEMENT_PROPERTIES__NEUTRAL,
    )


class ExplanationMinorBlock(Renderer[MinorBlock]):
    def __init__(self,
                 explanation: SequenceRenderer[LineElement],
                 ):
        self._explanation = explanation

    def render(self) -> MinorBlock:
        return MinorBlock(
            self._explanation.render_sequence(),
            text_struct.ELEMENT_PROPERTIES__INDENTED,
        )


class HeaderAndPathMinorBlocks(SequenceRenderer[MinorBlock]):
    def __init__(self,
                 header: Renderer[MinorBlock],
                 path: PathRepresentationsRenderers,
                 explanation: Optional[SequenceRenderer[LineElement]] = None,
                 ):
        self._header = header
        self._path = path
        self._explanation = explanation

    @staticmethod
    def of_string_header(header: ToStringObject,
                         path: PathDescriberForPrimitive) -> SequenceRenderer[MinorBlock]:
        return HeaderAndPathMinorBlocks(
            header_rendering.SimpleHeaderMinorBlockRenderer(
                header
            ),
            PathRepresentationsRenderersForPrimitive(path),
        )

    def render_sequence(self) -> Sequence[MinorBlock]:
        ret_val = [
            self._header.render(),
            PathMinorBlock(self._path).render(),
        ]
        if self._explanation is not None:
            ret_val.append(ExplanationMinorBlock(self._explanation).render())

        return ret_val


class HeaderAndPathMajorBlock(Renderer[MajorBlock]):
    def __init__(self,
                 header: Renderer[MinorBlock],
                 path: PathRepresentationsRenderers,
                 explanation: Optional[SequenceRenderer[LineElement]] = None,
                 ):
        self._header = header
        self._path = path
        self._explanation = explanation

    def render(self) -> MajorBlock:
        minor_blocks_renderer = HeaderAndPathMinorBlocks(self._header,
                                                         self._path,
                                                         self._explanation)
        return MajorBlock(
            minor_blocks_renderer.render_sequence()
        )


class HeaderAndPathMajorBlocks(SequenceRenderer[MajorBlock]):
    def __init__(self,
                 header: Renderer[MinorBlock],
                 path: PathRepresentationsRenderers,
                 explanation: Optional[SequenceRenderer[LineElement]] = None,
                 ):
        self._header = header
        self._path = path
        self._explanation = explanation

    def render_sequence(self) -> Sequence[MajorBlock]:
        major_block_renderer = HeaderAndPathMajorBlock(self._header,
                                                       self._path,
                                                       self._explanation)
        return [
            major_block_renderer.render()
        ]
