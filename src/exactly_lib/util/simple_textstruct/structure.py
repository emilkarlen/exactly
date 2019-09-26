from abc import ABC
from typing import TypeVar, Sequence, Optional, Generic

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle

RET = TypeVar('RET')
ENV = TypeVar('ENV')


class ElementProperties:
    def __init__(self,
                 indentation: int,
                 color: Optional[ForegroundColor],
                 font_style: Optional[FontStyle] = None):
        self._indented = indentation
        if not isinstance(indentation, int):
            raise ValueError('indentation is not an int')
        self._color = color
        self._font_style = font_style

    @property
    def indentation(self) -> int:
        return self._indented

    @property
    def color(self) -> Optional[ForegroundColor]:
        return self._color

    @property
    def font_style(self) -> Optional[FontStyle]:
        return self._font_style


PLAIN_ELEMENT_PROPERTIES = ElementProperties(0, None)

INDENTED_ELEMENT_PROPERTIES = ElementProperties(1, None)


def indentation_properties(indentation: int) -> ElementProperties:
    return ElementProperties(indentation, None, None)


class Element(ABC):
    def __init__(self, properties: ElementProperties):
        self._properties = properties

    @property
    def properties(self) -> ElementProperties:
        return self._properties


class LineObject(ABC):
    """
    Renders as a new-line-ended.

    May span zero or more lines.
    """

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        pass


class LineElement(Element):
    """Something that is displayed on one or more (whole) lines"""

    def __init__(self,
                 line_object: LineObject,
                 properties: ElementProperties = PLAIN_ELEMENT_PROPERTIES):
        super().__init__(properties)
        self._line_object = line_object

    @property
    def line_object(self) -> LineObject:
        return self._line_object


class PreFormattedStringLineObject(LineObject):
    """A string that does not use the layout settings when printed."""

    def __init__(self,
                 string: str,
                 string_is_line_ended: bool
                 ):
        self._string = string
        self._string_is_line_ended = string_is_line_ended

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        return visitor.visit_pre_formatted(env, self)

    @property
    def string_is_line_ended(self) -> bool:
        return self._string_is_line_ended

    @property
    def string(self) -> str:
        return self._string


class StringLineObject(LineObject):
    """A string that does use the layout settings when printed."""

    def __init__(self,
                 string: str,
                 string_is_line_ended: bool = False
                 ):
        self._string = string
        self._string_is_line_ended = string_is_line_ended

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        return visitor.visit_string(env, self)

    @property
    def string_is_line_ended(self) -> bool:
        return self._string_is_line_ended

    @property
    def string(self) -> str:
        return self._string


class StringLinesObject(LineObject):
    """A sequence of strings that should be output as a sequence of lines."""

    def __init__(self, strings: Sequence[str]):
        self._strings = strings

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        return visitor.visit_string_lines(env, self)

    @property
    def strings(self) -> Sequence[str]:
        return self._strings


class LineObjectVisitor(Generic[ENV, RET], ABC):
    def visit_pre_formatted(self, env: ENV, x: PreFormattedStringLineObject) -> RET:
        pass

    def visit_string(self, env: ENV, x: StringLineObject) -> RET:
        pass

    def visit_string_lines(self, env: ENV, x: StringLinesObject) -> RET:
        pass


class MinorBlock(Element):
    def __init__(self,
                 parts: Sequence[LineElement],
                 properties: ElementProperties = PLAIN_ELEMENT_PROPERTIES):
        super().__init__(properties)
        self._parts = parts

    @property
    def parts(self) -> Sequence[LineElement]:
        return self._parts


class MajorBlock(Element):
    def __init__(self,
                 parts: Sequence[MinorBlock],
                 properties: ElementProperties = PLAIN_ELEMENT_PROPERTIES,
                 ):
        super().__init__(properties)
        self._parts = parts

    @property
    def parts(self) -> Sequence[MinorBlock]:
        return self._parts


class Document:
    def __init__(self, blocks: Sequence[MajorBlock]):
        self._blocks = blocks

    @property
    def blocks(self) -> Sequence[MajorBlock]:
        return self._blocks


def minor_block_from_lines(lines: Sequence[LineObject],
                           block_properties: ElementProperties = PLAIN_ELEMENT_PROPERTIES) -> MinorBlock:
    return MinorBlock(
        [
            LineElement(line_object)
            for line_object in lines
        ],
        block_properties
    )
