from abc import ABC
from typing import Sequence

from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class TraceDoc(ABC):
    """Something that can be displayed as text, to describe execution or structure."""

    def render(self) -> Sequence[MajorBlock]:
        pass


class TraceDocProducer(ABC):
    """Something that can produce a TraceDoc"""

    def produce(self) -> TraceDoc:
        pass


class PreFormatted(TraceDoc):
    """A :class:TraceDoc that is a pre formatted string."""

    def __init__(self,
                 text: str,
                 is_line_ended: bool):
        """

        :param text: The pre formatted string
        :param is_line_ended: Tells if the string ends with a new-line.
        """
        self._is_line_ended = is_line_ended
        self._text = text

    @property
    def is_new_line_ended(self) -> bool:
        return self._is_line_ended

    @property
    def text(self) -> str:
        return self._text

    def render(self) -> Sequence[MajorBlock]:
        return [
            MajorBlock(
                structure.PLAIN_BLOCK_PROPERTIES,
                [structure.MinorBlock(
                    structure.PLAIN_BLOCK_PROPERTIES,
                    [structure.PreFormattedStringLineObject(self._text,
                                                            self._is_line_ended)])],
            )
        ]
