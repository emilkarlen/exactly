from typing import Any, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg import header_rendering, path_rendering
from exactly_lib.type_system.data.path_describer import PathDescriberForDdv, PathDescriberForPrimitive
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


def line_header_block__primitive(header: Any,
                                 path: PathDescriberForPrimitive,
                                 explanation: Optional[SequenceRenderer[LineElement]] = None,
                                 ) -> Renderer[MajorBlock]:
    return path_rendering.HeaderAndPathMajorBlock(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForPrimitive(path),
        explanation,
    )
