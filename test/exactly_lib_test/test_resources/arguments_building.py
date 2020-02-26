import itertools
from abc import ABC, abstractmethod
from typing import Sequence, List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_resources.strings import WithToString


class ArgumentElementsRenderer(ABC):
    """
    Base class for renderer of CLI argument strings.

    The string is rendered by __str__ or `arguments`.
    """

    def __str__(self):
        return ' '.join([str(element) for element in self.elements])

    @property
    @abstractmethod
    def elements(self) -> List[WithToString]:
        pass

    @property
    def as_str(self) -> str:
        """Alternative way to render as string."""
        return str(self)

    @property
    def as_arguments(self) -> Arguments:
        return Arguments(str(self))

    @property
    def as_argument_elements(self) -> ArgumentElements:
        return ArgumentElements(self.elements)

    @property
    def as_remaining_source(self) -> ParseSource:
        return parse_source.remaining_source(str(self))


class FromArgumentElementsBase(ArgumentElementsRenderer, ABC):
    @property
    def elements(self) -> List[WithToString]:
        raise NotImplementedError('unsupported')

    @property
    def as_str(self) -> str:
        return self.as_argument_elements.as_arguments.as_single_string

    @property
    def as_arguments(self) -> Arguments:
        return self.as_argument_elements.as_arguments

    @property
    @abstractmethod
    def as_argument_elements(self) -> ArgumentElements:
        pass

    @property
    def as_remaining_source(self) -> ParseSource:
        return self.as_argument_elements.as_remaining_source


class EmptyArgument(ArgumentElementsRenderer):
    """
    An empty string.
    """

    def __str__(self) -> str:
        return ''

    @property
    def elements(self) -> List[WithToString]:
        return []


class Singleton(ArgumentElementsRenderer):
    def __init__(self, value: WithToString):
        self.value = value

    @property
    def elements(self) -> List[WithToString]:
        return [self.value]


NEW_LINE = Singleton('\n')


class SequenceOfElementsBase(ArgumentElementsRenderer, ABC):
    """
    A sequence of arguments separated by space.
    """

    def __str__(self) -> str:
        return ' '.join(map(str, self.elements))


class SequenceOfElements(SequenceOfElementsBase):
    """
    A sequence of elements separated by space.
    """

    def __init__(self, elements: Sequence[WithToString]):
        self._elements = elements

    @property
    def elements(self) -> List[WithToString]:
        return list(self._elements)


class SequenceOfArguments(SequenceOfElementsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, arguments: Sequence[ArgumentElementsRenderer]):
        self._arguments = arguments

    @property
    def elements(self) -> List[WithToString]:
        return list(itertools.chain.from_iterable([
            argument.elements
            for argument in self._arguments
        ]))


class SequenceOfElementsSeparatedByElement(SequenceOfElementsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, separator: WithToString, elements: Sequence[WithToString]):
        self.separator = separator
        self._elements = elements

    @property
    def elements(self) -> List[WithToString]:
        if not self._elements:
            return []

        ret_val = [self._elements[0]]
        for extra_arg in self._elements[1:]:
            ret_val += [self.separator, extra_arg]

        return ret_val


class QuotedStringArgument(ArgumentElementsRenderer):
    def __init__(self,
                 string_value: str,
                 quote_type: QuoteType = QuoteType.HARD):
        self.string_value = string_value
        self.quote_type = quote_type

    def __str__(self):
        quote_char = QUOTE_CHAR_FOR_TYPE[self.quote_type]
        return quote_char + self.string_value + quote_char

    @property
    def elements(self) -> List[WithToString]:
        return [self]


class OptionArgument(ArgumentElementsRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: OptionName):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.option_syntax(self.option_name)

    @property
    def elements(self) -> List[WithToString]:
        return [self]


class CustomOptionArgument(ArgumentElementsRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: str):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.long_option_syntax(self.option_name)

    @property
    def elements(self) -> List[WithToString]:
        return [self]


class OptionWithArgument(SequenceOfElementsBase):
    """
    Renders an option with mandatory argument
    """

    def __init__(self, option_name: OptionName, option_argument: Sequence[WithToString]):
        self.option_name = option_name
        self.option_argument = option_argument

    @property
    def elements(self) -> List[WithToString]:
        return [OptionArgument(self.option_name), self.option_argument]
