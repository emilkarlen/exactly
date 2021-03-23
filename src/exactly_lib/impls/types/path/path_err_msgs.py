from typing import Any, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.text_render import header_rendering
from exactly_lib.impls.types.path import path_rendering
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.path_describer import PathDescriberForDdv, PathDescriberForPrimitive
from exactly_lib.util.render.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.structure import LineElement, MajorBlock


def line_header__ddv(header: Any,
                     path: PathDescriberForDdv,
                     explanation: Optional[SequenceRenderer[LineElement]] = None,
                     ) -> TextRenderer:
    return path_rendering.HeaderAndPathMajorBlocks(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForDdv(path),
        explanation,
    )


def line_header__primitive(header: Any,
                           path: PathDescriberForPrimitive,
                           explanation: Optional[SequenceRenderer[LineElement]] = None,
                           ) -> TextRenderer:
    return path_rendering.HeaderAndPathMajorBlocks(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForPrimitive(path),
        explanation,
    )


def line_header__primitive__path(header: Any,
                                 path: DescribedPath,
                                 explanation: Optional[SequenceRenderer[LineElement]] = None,
                                 ) -> TextRenderer:
    return line_header__primitive(
        header,
        path.describer,
        explanation,
    )


def line_header_block__primitive(header: Any,
                                 path: PathDescriberForPrimitive,
                                 explanation: Optional[SequenceRenderer[LineElement]] = None,
                                 ) -> Renderer[MajorBlock]:
    return path_rendering.HeaderAndPathMajorBlock(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForPrimitive(path),
        explanation,
    )


def line_header_block__primitive__path(header: Any,
                                       path: DescribedPath,
                                       explanation: Optional[SequenceRenderer[LineElement]] = None,
                                       ) -> Renderer[MajorBlock]:
    return line_header_block__primitive(
        header,
        path.describer,
        explanation,
    )
