from abc import ABC
from typing import TypeVar, Sequence, Optional, Generic

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle

RET = TypeVar('RET')
ENV = TypeVar('ENV')


class Indentation(tuple):
    def __new__(cls,
                level: int = 0,
                suffix: str = '',
                ):
        return tuple.__new__(cls, (level, suffix))

    @property
    def level(self) -> int:
        return self[0]

    @property
    def suffix(self) -> str:
        return self[1]


INDENTATION__NEUTRAL = Indentation(0, '')
INDENTATION__1 = Indentation(1, '')


class TextStyle(tuple):
    def __new__(cls,
                color: Optional[ForegroundColor] = None,
                font_style: Optional[FontStyle] = None,
                ):
        return tuple.__new__(cls, (color, font_style))

    @property
    def color(self) -> Optional[ForegroundColor]:
        return self[0]

    @property
    def font_style(self) -> Optional[FontStyle]:
        return self[1]


TEXT_STYLE__NEUTRAL = TextStyle(None, None)


class ElementProperties(tuple):
    def __new__(cls,
                indentation: Indentation = INDENTATION__NEUTRAL,
                text_style: TextStyle = TEXT_STYLE__NEUTRAL,
                ):
        return tuple.__new__(cls, (indentation, text_style))

    @property
    def indentation(self) -> Indentation:
        return self[0]

    @property
    def text_style(self) -> TextStyle:
        return self[1]

    @property
    def indentation_level(self) -> int:
        return self[0].level

    @property
    def with_increased_indentation_level(self) -> 'ElementProperties':
        i = self[0]
        return ElementProperties(
            Indentation(i.level + 1,
                        i.suffix),
            self[1],
        )

    def with_increased_indentation(self, increment: Indentation) -> 'ElementProperties':
        i = self[0]
        return ElementProperties(
            Indentation(i.level + increment.level,
                        i.suffix + increment.suffix),
            self[1],
        )

    @property
    def color(self) -> Optional[ForegroundColor]:
        return self[1].color

    @property
    def font_style(self) -> Optional[FontStyle]:
        return self[1].font_style


ELEMENT_PROPERTIES__NEUTRAL = ElementProperties(INDENTATION__NEUTRAL,
                                                TEXT_STYLE__NEUTRAL)

ELEMENT_PROPERTIES__INDENTED = ElementProperties(Indentation(1, ''),
                                                 TEXT_STYLE__NEUTRAL)


def indentation_properties(level: int) -> ElementProperties:
    return ElementProperties(Indentation(level, ''),
                             TEXT_STYLE__NEUTRAL)


class Element(ABC):
    """Mutable element with ElementProperties"""

    def __init__(self, properties: ElementProperties):
        self._properties = properties

    @property
    def properties(self) -> ElementProperties:
        return self._properties

    def set_properties(self, properties: ElementProperties):
        self._properties = properties


class LineObject(ABC):
    """
    Renders as a new-line-ended.

    May span zero or more lines.
    """

    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        pass


class LineElement(Element):
    """
    Something that is displayed on one or more (whole) lines

    Mutable container of a LineObject.
    """

    def __init__(self,
                 line_object: LineObject,
                 properties: ElementProperties = ELEMENT_PROPERTIES__NEUTRAL):
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
    """Mutable container of a sequence of LineElement"""

    def __init__(self,
                 parts: Sequence[LineElement],
                 properties: ElementProperties = ELEMENT_PROPERTIES__NEUTRAL):
        super().__init__(properties)
        self._parts = parts

    @property
    def parts(self) -> Sequence[LineElement]:
        return self._parts


class MajorBlock(Element):
    """Mutable container of a sequence of MinorBlock"""

    def __init__(self,
                 parts: Sequence[MinorBlock],
                 properties: ElementProperties = ELEMENT_PROPERTIES__NEUTRAL,
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
                           block_properties: ElementProperties = ELEMENT_PROPERTIES__NEUTRAL) -> MinorBlock:
    return MinorBlock(
        [
            LineElement(line_object)
            for line_object in lines
        ],
        block_properties
    )
