from typing import Any, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering import \
    component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import LineElement, MajorBlock
from exactly_lib.util.str_ import str_constructor


def single_pre_formatted_line_object(x: Any,
                                     is_line_ended: bool = False) -> TextRenderer:
    """
    :param is_line_ended: Tells if the string str(x) ends with a new-line character.
    :param x: __str__ gives the string
    """
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString(x, is_line_ended)
    )


def os_exception_error_message(ex: OSError) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString(
            str_constructor.FormatMap(
                _OS_EXCEPTION_ERROR_MESSAGE,
                {
                    'msg': ex.strerror,
                    'errno': ex.errno,
                    'filename': ex.filename,
                    'filename2': ex.filename2,
                }
            )
        )
    )


def single_line(x: Any) -> TextRenderer:
    """
    :param x: __str__ gives the string
    """
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.StringLineObject(x)
    )


def plain_line_elements_of_string_lines(lines: Sequence[str]) -> SequenceRenderer[LineElement]:
    return rend_comb.ConstantSequenceR([
        LineElement(text_struct.StringLineObject(line))
        for line in lines
    ])


def major_blocks_of_string_lines(lines: Sequence[str]) -> SequenceRenderer[MajorBlock]:
    return rend_comb.SingletonSequenceR(
        comp_rend.MajorBlockR(
            rend_comb.SingletonSequenceR(
                comp_rend.MinorBlockR(
                    plain_line_elements_of_string_lines(lines)
                )
            )
        )
    )


_OS_EXCEPTION_ERROR_MESSAGE = """\
{msg}

errno={errno}

filename={filename}
filename2={filename2}
"""
