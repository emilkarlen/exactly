import itertools
from typing import Iterator


def int_strings(start: int, width: int) -> Iterator[str]:
    """
    Gives an iterator of unique strings - integers of width "width", padded with '0's
    """
    return (
        str(n).zfill(width)
        for n in itertools.count(start)
    )
