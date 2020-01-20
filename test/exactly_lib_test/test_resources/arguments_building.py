from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_resources.matcher_argument import ArgumentList

Stringable = TypeVar('Stringable')


class ArgumentElementRenderer(ABC):
    """
    Base class for renderer of CLI argument strings.

    The string is rendered by __str__ or `arguments`.
    """

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def arguments(self) -> List[Stringable]:
        pass

    @property
    def as_str(self) -> str:
        """Alternative way to render as string."""
        return str(self)

    @property
    def as_arguments(self) -> Arguments:
        return Arguments(' '.join(self.arguments))

    @property
    def as_argument_elements(self) -> ArgumentElements:
        return ArgumentElements(self.arguments)

    @property
    def as_remaining_source(self) -> ParseSource:
        return parse_source.remaining_source(str(self))


class OfArgumentList(ArgumentElementRenderer):
    def __init__(self, argument_list: ArgumentList):
        self.argument_list = argument_list

    def __str__(self) -> str:
        return str(self.argument_list)

    @property
    def arguments(self) -> List[Stringable]:
        return self.argument_list.elements


class EmptyArgument(ArgumentElementRenderer):
    """
    An empty string.
    """

    def __str__(self) -> str:
        return ''

    @property
    def arguments(self) -> List[Stringable]:
        return []


class SequenceOfArgumentsBase(ArgumentElementRenderer):
    """
    A sequence of arguments separated by space.
    """

    @property
    def arguments(self) -> List[Stringable]:
        raise NotImplementedError('abstract method')

    def __str__(self) -> str:
        return ' '.join(map(str, self.arguments))


class SequenceOfArguments(SequenceOfArgumentsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, arguments: Sequence[Stringable]):
        self._arguments = arguments

    @property
    def arguments(self) -> List[Stringable]:
        return list(self._arguments)


class SequenceOfArgumentsSeparatedByArgument(SequenceOfArgumentsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, separator: Stringable, arguments: Sequence[Stringable]):
        self.separator = separator
        self._arguments = arguments

    @property
    def arguments(self) -> List[Stringable]:
        if not self._arguments:
            return []

        ret_val = [self._arguments[0]]
        for extra_arg in self._arguments[1:]:
            ret_val += [self.separator, extra_arg]

        return ret_val


class QuotedStringArgument(ArgumentElementRenderer):
    def __init__(self,
                 string_value: str,
                 quote_type: QuoteType = QuoteType.HARD):
        self.string_value = string_value
        self.quote_type = quote_type

    def __str__(self):
        quote_char = QUOTE_CHAR_FOR_TYPE[self.quote_type]
        return quote_char + self.string_value + quote_char

    @property
    def arguments(self) -> List[Stringable]:
        return [self]


class OptionArgument(ArgumentElementRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: OptionName):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.option_syntax(self.option_name)

    @property
    def arguments(self) -> List[Stringable]:
        return [self]


class CustomOptionArgument(ArgumentElementRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: str):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.long_option_syntax(self.option_name)

    @property
    def arguments(self) -> List[Stringable]:
        return [str(self)]


class OptionWithArgument(SequenceOfArgumentsBase):
    """
    Renders an option with mandatory argument
    """

    def __init__(self, option_name: OptionName, option_argument: Sequence[Stringable]):
        self.option_name = option_name
        self.option_argument = option_argument

    @property
    def arguments(self) -> List[Stringable]:
        return [OptionArgument(self.option_name), self.option_argument]
