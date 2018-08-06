from typing import List

SOURCE_LINE_INDENT = '  '
Block = List[str]
Blocks = List[Block]


def single_str_block(s: str) -> Block:
    return [s]
