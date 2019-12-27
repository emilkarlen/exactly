from abc import ABC, abstractmethod
from typing import Optional, Any, Sequence, List

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive, PathDescriberForDdv
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement


class PathRepresentationsRenderers(ABC):
    """Gives renderers for each path representation that should be displayed"""

    @abstractmethod
    def renders(self) -> List[Renderer[str]]:
        pass


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


class PathDdvLines(SequenceRenderer[LineElement]):
    def __init__(self,
                 path: PathDescriberForPrimitive,
                 header_line: Optional[Any] = None
                 ):
        self._path = path
        self._header_line = header_line

    def render_sequence(self) -> Sequence[LineElement]:
        ret_val = [LineElement(text_struct.StringLineObject(self._path.value.render()))]
        if self._header_line is not None:
            header = LineElement(text_struct.StringLineObject(self._header_line))
            ret_val.insert(0, header)

        return ret_val


class PathDdvMinorBlock(Renderer[MinorBlock]):
    def __init__(self,
                 path: PathDescriberForPrimitive,
                 header_line: Optional[Any] = None
                 ):
        self._path = path
        self._header_line = header_line

    def render(self) -> MinorBlock:
        return MinorBlock(
            PathDdvLines(self._path,
                         self._header_line).render_sequence()
        )


def path_renderers(path: PathDescriberForPrimitive) -> List[Renderer[str]]:
    return (
        [path.value, path.primitive]
        if path.resolving_dependency is DirectoryStructurePartition.HDS
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
            text_struct.ELEMENT_PROPERTIES__INDENTED,
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
