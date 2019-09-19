from typing import Any, Sequence

from exactly_lib.common.err_msg.definitions import Blocks, Block
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering import \
    renderer_combinators as rend_comb, \
    component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, PreFormattedStringLineObject, \
    MajorBlock, LineObject


def single_pre_formatted_line_object(x: Any,
                                     is_line_ended: bool = False) -> TextRenderer:
    """
    :param is_line_ended: Tells if the string str(x) ends with a new-line character.
    :param x: __str__ gives the string
    """
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString(x, is_line_ended)
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


def of_err_msg_resolver(resolver: ErrorMessageResolver) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        _ErrorMessageResolverLineObject(resolver)
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


class _ErrorMessageResolverLineObject(LineObjectRenderer):
    def __init__(self, resolver: ErrorMessageResolver):
        self._resolver = resolver

    def render(self) -> LineObject:
        return PreFormattedStringLineObject(self._resolver.resolve(),
                                            False)
