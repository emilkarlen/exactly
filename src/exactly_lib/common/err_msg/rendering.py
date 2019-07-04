import functools
from typing import List

from exactly_lib.common.err_msg.definitions import Blocks
from exactly_lib.util import file_printables
from exactly_lib.util.collection import intersperse_list
from exactly_lib.util.file_printer import FilePrintable


def blocks_as_lines(blocks: Blocks) -> List[str]:
    return functools.reduce(lambda x, y: x + y,
                            intersperse_list([''], blocks),
                            [])


def blocks_as_str(blocks: Blocks) -> str:
    return '\n'.join(blocks_as_lines(blocks))


def blocks_as_printable(blocks: Blocks) -> FilePrintable:
    return file_printables.of_string(blocks_as_str(blocks))
