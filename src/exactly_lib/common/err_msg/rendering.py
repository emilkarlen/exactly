import functools
from typing import List

from exactly_lib.common.err_msg.definitions import Blocks
from exactly_lib.util.collection import intersperse_list


def blocks_as_lines(blocks: Blocks) -> List[str]:
    return functools.reduce(lambda x, y: x + y,
                            intersperse_list([''], blocks),
                            [])
