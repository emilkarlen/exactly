from typing import Any, Sequence

from exactly_lib.common.err_msg.definitions import Blocks, Block
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util import strings
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering import \
    component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, PreFormattedStringLineObject, \
    MajorBlock


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
            strings.FormatMap(
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


def minor_blocks_of_string_blocks(contents: Blocks) -> SequenceRenderer[MinorBlock]:
    return _OfBlocks(contents)


def major_block_of_string_blocks(contents: Blocks) -> Renderer[MajorBlock]:
    return comp_rend.MajorBlockR(minor_blocks_of_string_blocks(contents))


def major_blocks_of_string_blocks(contents: Blocks) -> SequenceRenderer[MajorBlock]:
    return rend_comb.SingletonSequenceR(
        major_block_of_string_blocks(contents)
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


class _OfBlocks(SequenceRenderer[MinorBlock]):
    def __init__(self, contents: Blocks):
        self._contents = contents

    def render_sequence(self) -> Sequence[MinorBlock]:
        return [
            _mk_minor_block(lines)
            for lines in self._contents
        ]


def _mk_minor_block(lines: Block) -> MinorBlock:
    return MinorBlock([
        LineElement(
            PreFormattedStringLineObject(line, False)
        )
        for line in lines
    ]
    )


_OS_EXCEPTION_ERROR_MESSAGE = """\
{msg}

errno={errno}

filename={filename}
filename2={filename2}
"""
