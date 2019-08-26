from typing import Any, Sequence, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2 import header_rendering, path_rendering
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForValue, PathDescriberForPrimitive
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import LineElement


def line_header__value(header: Any,
                       path: PathDescriberForValue,
                       explanation: Optional[Renderer[Sequence[LineElement]]] = None,
                       ) -> TextRenderer:
    return path_rendering.HeaderAndPathMajorBlocks(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForValue(path),
        explanation,
    )


def line_header__primitive(header: Any,
                           path: PathDescriberForPrimitive,
                           explanation: Optional[Renderer[Sequence[LineElement]]] = None,
                           ) -> TextRenderer:
    return path_rendering.HeaderAndPathMajorBlocks(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForPrimitive(path),
        explanation,
    )
