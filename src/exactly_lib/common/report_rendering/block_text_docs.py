"""Deprecated formatting utils"""
from typing import Sequence

from exactly_lib.common.err_msg.definitions import Blocks, Block
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MinorBlock, MajorBlock, LineElement, \
    PreFormattedStringLineObject


def minor_blocks_of_string_blocks(contents: Blocks) -> SequenceRenderer[MinorBlock]:
    return _OfBlocks(contents)


def major_block_of_string_blocks(contents: Blocks) -> Renderer[MajorBlock]:
    return comp_rend.MajorBlockR(minor_blocks_of_string_blocks(contents))


def major_blocks_of_string_blocks(contents: Blocks) -> SequenceRenderer[MajorBlock]:
    return rend_comb.SingletonSequenceR(
        major_block_of_string_blocks(contents)
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
