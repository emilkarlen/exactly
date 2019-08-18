from typing import Optional, Any, Sequence

from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForPrimitive
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement


def path_value_major_block_renderer(path: PathDescriberForPrimitive,
                                    header_line: Optional[Any] = None) -> Renderer[MajorBlock]:
    return PathValueMajorBlock(path, header_line)


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


class PathValueMajorBlock(Renderer[MajorBlock]):
    def __init__(self,
                 path: PathDescriberForPrimitive,
                 header_line: Optional[Any] = None
                 ):
        self._path = path
        self._header_line = header_line

    def render(self) -> MajorBlock:
        return MajorBlock([
            PathValueMinorBlock(self._path,
                                self._header_line).render()

        ]
        )
