from typing import List

SOURCE_LINE_INDENT = '  '
Block = List[str]  # Sequence[LineObject]
Blocks = List[Block]  # MinorBlock


def single_str_block(s: str) -> Block:
    return [s]
