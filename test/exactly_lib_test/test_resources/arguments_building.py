from typing import Sequence

from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements.argument import OptionName


class ArgumentElementRenderer:
    """
    Base class for renderer of CLI argument strings.

    This class is just a helper for easily finding implementations
    via sub classing.

    The string is rendered by __str__.
    """

    def __str__(self) -> str:
        raise NotImplementedError('must be implemented by sub classes')


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
    def arguments(self) -> Sequence:
        raise NotImplementedError('abstract method')

    def __str__(self) -> str:
        return ' '.join(map(str, self.arguments))


class SequenceOfArguments(SequenceOfArgumentsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, arguments: Sequence):
        self._arguments = arguments

    @property
    def arguments(self) -> Sequence:
        return self._arguments


class SequenceOfArgumentsSeparatedByArgument(SequenceOfArgumentsBase):
    """
    A sequence of arguments separated by space.
    """

    def __init__(self, separator, arguments: Sequence):
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


class OptionArgument(ArgumentElementRenderer):
    """
    Renders an option
    """

    def __init__(self, option_name: OptionName):
        self.option_name = option_name

    def __str__(self) -> str:
        return option_syntax.option_syntax(self.option_name)


class OptionWithArgument(SequenceOfArgumentsBase):
    """
    Renders an option with mandatory argument
    """

    def __init__(self, option_name: OptionName, option_argument):
        self.option_name = option_name
        self.option_argument = option_argument

    @property
    def arguments(self) -> Sequence:
        return [OptionArgument(self.option_name), self.option_argument]
