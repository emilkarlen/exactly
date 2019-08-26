from typing import Any

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2 import header_rendering, path_rendering
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForValue, PathDescriberForPrimitive


def line_header__value(header: Any,
                       path: PathDescriberForValue) -> TextRenderer:
    return path_rendering.HeaderAndPathMajorBlocks(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForValue(path)
    )


def line_header__primitive(header: Any,
                           path: PathDescriberForPrimitive) -> TextRenderer:
    return path_rendering.HeaderAndPathMajorBlocks(
        header_rendering.SimpleHeaderMinorBlockRenderer(header),
        path_rendering.PathRepresentationsRenderersForPrimitive(path)
    )
