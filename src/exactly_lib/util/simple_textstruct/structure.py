from abc import ABC
from typing import TypeVar, Sequence, Optional, Generic

from exactly_lib.util.ansi_terminal_color import ForegroundColor

RET = TypeVar('RET')
ENV = TypeVar('ENV')


class LineObject(ABC):
    """Something that is displayed on one or more (whole) lines"""

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        pass


class PreFormattedStringLineObject(LineObject):
    def __init__(self,
                 string: str,
                 is_line_ended: bool
                 ):
        self._string = string
        self._is_line_ended = is_line_ended

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        return visitor.visit_pre_formatted(env, self)

    @property
    def is_new_line_ended(self) -> bool:
        return self._is_line_ended

    @property
    def string(self) -> str:
        return self._string


class LineObjectVisitor(Generic[ENV, RET], ABC):
    def visit_pre_formatted(self, env: ENV, x: PreFormattedStringLineObject) -> RET:
        pass


class BlockProperties:
    def __init__(self,
                 indented: bool,
                 color: Optional[ForegroundColor]):
        self.color = color
        self.indented = indented


PLAIN_BLOCK_PROPERTIES = BlockProperties(False, None)


class MinorBlock:
    def __init__(self,
                 properties: BlockProperties,
                 parts: Sequence[LineObject]):
        self._properties = properties
        self._parts = parts

    @property
    def properties(self) -> BlockProperties:
        return self._properties

    @property
    def parts(self) -> Sequence[LineObject]:
        return self._parts


class MajorBlock:
    def __init__(self,
                 properties: BlockProperties,
                 parts: Sequence[MinorBlock]):
        self._properties = properties
        self._parts = parts

    @property
    def properties(self) -> BlockProperties:
        return self._properties

    @property
    def parts(self) -> Sequence[MinorBlock]:
        return self._parts


class MajorBlocksRenderer(ABC):
    def render(self) -> Sequence[MajorBlock]:
        pass
