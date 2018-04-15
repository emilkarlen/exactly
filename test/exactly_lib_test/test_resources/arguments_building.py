from typing import Sequence, TypeVar

from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE

Stringable = TypeVar('Stringable')


class ArgumentElementRenderer:
    """
    Base class for renderer of CLI argument strings.

    This class is just a helper for easily finding implementations
    via sub classing.

    The string is rendered by __str__.
    """

    def __str__(self) -> str:
        raise NotImplementedError('must be implemented by sub classes')

    @property
    def as_str(self) -> str:
        """Alternative way to render as string."""
        return str(self)


class EmptyArgument(ArgumentElementRenderer):
    """
    An empty string.
    """

    def __str__(self) -> str:
        return ''


class SequenceOfArgumentsBase(ArgumentElementRenderer):
    """
    A sequence of arguments separated by space.
    """

    @property
    def arguments(self) -> Sequence[Stringable]:
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
    def arguments(self) -> Sequence:
        return self._arguments


class SequenceOfArgumentsSeparatedByArgument(SequenceOfArgumentsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, separator: Stringable, arguments: Sequence[Stringable]):
        self.separator = separator
        self._arguments = arguments

    @property
    def arguments(self) -> Sequence:
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


class OptionArgument(ArgumentElementRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: OptionName):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.option_syntax(self.option_name)


class CustomOptionArgument(ArgumentElementRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: str):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.long_option_syntax(self.option_name)


class OptionWithArgument(SequenceOfArgumentsBase):
    """
    Renders an option with mandatory argument
    """

    def __init__(self, option_name: OptionName, option_argument: Sequence[Stringable]):
        self.option_name = option_name
        self.option_argument = option_argument

    @property
    def arguments(self) -> Sequence:
        return [OptionArgument(self.option_name), self.option_argument]
