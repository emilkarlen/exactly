import enum
from abc import ABC, abstractmethod
from typing import Sequence, AbstractSet

from exactly_lib.util.name_and_value import NameAndValue


class LayoutSpec:
    def __init__(self,
                 optional_new_line: Sequence[str],
                 symbol_reference_as_plain_symbol_name: bool = False,
                 token_separator: str = ' ',
                 ):
        """
        :param optional_new_line: The layout of optional new lines
        :param symbol_reference_as_plain_symbol_name: For symbol references
        who's syntax allow both plain name and symbol reference syntax:
        layout as plain symbol name.
        """
        self._optional_new_line = optional_new_line
        self._symbol_reference_as_plain_symbol_name = symbol_reference_as_plain_symbol_name
        self._token_separator = token_separator

    @staticmethod
    def of_default() -> 'LayoutSpec':
        return LayoutSpec((), True, ' ')

    @staticmethod
    def of_alternative() -> 'LayoutSpec':
        return LayoutSpec(('\n',), False, '\t')

    @property
    def optional_new_line(self) -> Sequence[str]:
        return self._optional_new_line

    @property
    def symbol_reference_as_plain_symbol_name(self) -> bool:
        return self._symbol_reference_as_plain_symbol_name

    @property
    def token_separator(self) -> str:
        return self._token_separator


class TokenPosition(enum.Enum):
    FIRST = 1
    LAST = 2


class LayoutAble(ABC):
    @abstractmethod
    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        pass


STANDARD_LAYOUT_SPECS = (
    NameAndValue('default', LayoutSpec.of_default()),
    NameAndValue('alternative', LayoutSpec.of_alternative()),
)


class _OptionalNewLine(LayoutAble):
    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        return spec.optional_new_line


class _NewLineIfNotFirstOrLast(LayoutAble):
    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        return (
            ['\n']
            if len(position) == 0
            else
            []
        )


OPTIONAL_NEW_LINE = _OptionalNewLine()
NEW_LINE_IF_NOT_FIRST_OR_LAST = _NewLineIfNotFirstOrLast()
