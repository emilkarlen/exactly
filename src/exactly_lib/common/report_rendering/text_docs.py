from typing import Any

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects


def single_pre_formatted_line_object(x: Any) -> TextRenderer:
    """
    :param x: __str__ gives the string
    """
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString(x)
    )


def single_pre_formatted_line_object__from_fp(fp: FilePrintable) -> TextRenderer:
    return single_pre_formatted_line_object(file_printables.print_to_string(fp))
