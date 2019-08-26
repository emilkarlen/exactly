from abc import ABC, abstractmethod
from typing import Optional, Any, Sequence, List

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForPrimitive, PathDescriberForValue
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement


class PathRepresentationsRenderers(ABC):
    """Gives renderers for each path representation that should be displayed"""

    @abstractmethod
    def renders(self) -> List[Renderer[str]]:
        pass


class PathRepresentationsRenderersForValue(PathRepresentationsRenderers):
    def __init__(self, path: PathDescriberForValue):
        self._path = path

    def renders(self) -> List[Renderer[str]]:
        return [self._path.value]


class PathRepresentationsRenderersForPrimitive(PathRepresentationsRenderers):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def renders(self) -> List[Renderer[str]]:
        p = self._path
        return (
            [p.value, p.primitive]
            if p.resolving_dependency is DirectoryStructurePartition.HOME
            else
            [p.value]
        )


class PathValueLines(SequenceRenderer[LineElement]):
    def __init__(self,
                 path: PathDescriberForPrimitive,
                 header_line: Optional[Any] = None
                 ):
        self._path = path
        self._header_line = header_line

    def render(self) -> Sequence[LineElement]:
        ret_val = [LineElement(text_struct.StringLineObject(self._path.value.render()))]
        if self._header_line is not None:
            header = LineElement(text_struct.StringLineObject(self._header_line))
            ret_val.insert(0, header)

        return ret_val


class PathValueMinorBlock(Renderer[MinorBlock]):
    def __init__(self,
                 path: PathDescriberForPrimitive,
                 header_line: Optional[Any] = None
                 ):
        self._path = path
        self._header_line = header_line

    def render(self) -> MinorBlock:
        return MinorBlock(
            PathValueLines(self._path,
                           self._header_line).render()
        )


def path_renderers(path: PathDescriberForPrimitive) -> List[Renderer[str]]:
    return (
        [path.value, path.primitive]
        if path.resolving_dependency is DirectoryStructurePartition.HOME
        else [path.value]
    )


def path_strings(path: PathDescriberForPrimitive) -> List[str]:
    return [
        r.render()
        for r in path_renderers(path)
    ]


class PathMinorBlock(Renderer[MinorBlock]):
    def __init__(self,
                 path: PathRepresentationsRenderers,
                 ):
        self._path = path

    def render(self) -> MinorBlock:
        return MinorBlock([
            text_struct.LineElement(
                text_struct.StringLineObject(line.render())
            )
            for line in self._path.renders()
        ],
            text_struct.INDENTED_ELEMENT_PROPERTIES,
        )


class ExplanationMinorBlock(Renderer[MinorBlock]):
    def __init__(self,
                 explanation: Renderer[Sequence[LineElement]],
                 ):
        self._explanation = explanation

    def render(self) -> MinorBlock:
        return MinorBlock(
            self._explanation.render(),
            text_struct.INDENTED_ELEMENT_PROPERTIES,
        )


class HeaderAndPathMinorBlocks(Renderer[Sequence[MinorBlock]]):
    def __init__(self,
                 header: Renderer[MinorBlock],
                 path: PathRepresentationsRenderers,
                 explanation: Optional[Renderer[Sequence[LineElement]]] = None,
                 ):
        self._header = header
        self._path = path
        self._explanation = explanation

    def render(self) -> Sequence[MinorBlock]:
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
                 explanation: Optional[Renderer[Sequence[LineElement]]] = None,
                 ):
        self._header = header
        self._path = path
        self._explanation = explanation

    def render(self) -> MajorBlock:
        minor_blocks_renderer = HeaderAndPathMinorBlocks(self._header,
                                                         self._path,
                                                         self._explanation)
        return MajorBlock(
            minor_blocks_renderer.render()
        )


class HeaderAndPathMajorBlocks(SequenceRenderer[MajorBlock]):
    def __init__(self,
                 header: Renderer[MinorBlock],
                 path: PathRepresentationsRenderers,
                 explanation: Optional[Renderer[Sequence[LineElement]]] = None,
                 ):
        self._header = header
        self._path = path
        self._explanation = explanation

    def render(self) -> Sequence[MajorBlock]:
        major_block_renderer = HeaderAndPathMajorBlock(self._header,
                                                       self._path,
                                                       self._explanation)
        return [
            major_block_renderer.render()
        ]
