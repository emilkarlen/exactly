"""Deprecated formatting utils"""
from typing import List

SOURCE_LINE_INDENT = '  '
Block = List[str]  # Sequence[LineObject] / MinorBlock
Blocks = List[Block]  # MinorBlock / Sequence[MinorBlock]


def single_str_block(s: str) -> Block:
    return [s]
