from enum import Enum
from typing import Sequence


class Argument:
    pass


class Constant(Argument):
    """
    A constant string. E.g. "-" denoting stdin.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return '{}({})'.format(type(self), repr(self._name))


class Named(Argument):
    """
    A named element. May be a positional argument (such as "FILE"),
    or the name of a group of arguments, e.g.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return '{}({})'.format(type(self), repr(self._name))


class OptionName(tuple):
    """
    An option with a long name à la "find".
    """

    def __new__(cls,
                long_name: str = ''):
        return tuple.__new__(cls, ((long_name,)))

    @property
    def long(self) -> str:
        return self[0]

    def __str__(self):
        return '{}(short_name={}, long_name=)'.format(type(self), repr(self.long))


class Option(Argument):
    """
    A traditional command line option.
    """

    def __init__(self,
                 name: OptionName,
                 argument: str = ''):
        self._name = name
        self._argument = argument

    @property
    def name(self) -> OptionName:
        return self._name

    @property
    def long_name(self) -> str:
        return self._name.long

    @property
    def argument(self) -> str:
        """
        :return: Empty `str` if option does not have an argument.
        """
        return self._argument

    def __str__(self):
        return '{}(name={}, argument={})'.format(type(self), repr(self._name), str(self._argument))


class ShortAndLongOptionName(tuple):
    """
    An option with either a short name, a long name, or both.
    """

    def __new__(cls,
                short_name: str = '',
                long_name: str = ''):
        return tuple.__new__(cls, (short_name, long_name))

    @property
    def short(self) -> str:
        return self[0]

    @property
    def long(self) -> str:
        return self[1]

    def __str__(self):
        return '{}(short_name={}, long_name=)'.format(type(self), repr(self.short), repr(self.long))


class ShortAndLongOption(Argument):
    """
    A command line option with short and long variant, as understood by pythons CL argument parser.
    """

    def __init__(self,
                 name: ShortAndLongOptionName,
                 argument: str = ''):
        self._name = name
        self._argument = argument

    @property
    def name(self) -> ShortAndLongOptionName:
        return self._name

    @property
    def short_name(self) -> str:
        return self._name.short

    @property
    def long_name(self) -> str:
        return self._name.long

    @property
    def argument(self) -> str:
        """
        :return: Empty `str` if option does not have an argument.
        """
        return self._argument

    def __str__(self):
        return '{}(name={}, argument={})'.format(type(self), repr(self._name), str(self._argument))


def option(long_name: str = '',
           argument: str = '') -> Option:
    return Option(OptionName(long_name),
                  argument=argument)


def short_long_option(short_name: str = '',
                      long_name: str = '',
                      argument: str = '') -> ShortAndLongOption:
    return ShortAndLongOption(ShortAndLongOptionName(short_name=short_name,
                                                     long_name=long_name),
                              argument=argument)


class Multiplicity(Enum):
    OPTIONAL = 1
    MANDATORY = 2
    ZERO_OR_MORE = 3
    ONE_OR_MORE = 4


class ArgumentUsage:
    """
    How one or more `Argument`s are used.
    """

    def __init__(self,
                 multiplicity: Multiplicity):
        self._multiplicity = multiplicity

    @property
    def multiplicity(self) -> Multiplicity:
        return self._multiplicity


class Single(ArgumentUsage):
    """
    A single `Argument`
    """

    def __init__(self,
                 multiplicity: Multiplicity,
                 argument: Argument):
        super().__init__(multiplicity)
        self._argument = argument

    @property
    def argument(self) -> Argument:
        return self._argument

    def __str__(self):
        return '{}(multiplicity={}, argument={})'.format(type(self), repr(self._multiplicity), str(self._argument))


class Choice(ArgumentUsage):
    """
    A choice between two or more `Argument`s.
    """

    def __init__(self,
                 multiplicity: Multiplicity,
                 choices: Sequence[Sequence[Argument]]):
        super().__init__(multiplicity)
        self._choices = choices

    @staticmethod
    def of_single_argument_choices(
            multiplicity: Multiplicity,
            choices: Sequence[Argument]) -> 'Choice':
        return Choice(multiplicity,
                      [[argument] for argument in choices])

    @staticmethod
    def of_multiple_argument_choices(
            multiplicity: Multiplicity,
            choices: Sequence[Sequence[Argument]]) -> 'Choice':
        return Choice(multiplicity, choices)

    @staticmethod
    def of_multiple_single_argument_choices(
            multiplicity: Multiplicity,
            choices: Sequence[Argument]) -> 'Choice':
        return Choice(multiplicity, [(choice,) for choice in choices])

    @property
    def choices(self) -> Sequence[Sequence[Argument]]:
        return self._choices

    def __str__(self):
        return '{}(multiplicity={}, arguments={})'.format(type(self), repr(self._multiplicity), repr(self._choices))


class ArgumentVisitor:
    def visit(self, x: Argument):
        if isinstance(x, Constant):
            return self.visit_constant(x)
        if isinstance(x, Named):
            return self.visit_named(x)
        if isinstance(x, Option):
            return self.visit_option(x)
        if isinstance(x, ShortAndLongOption):
            return self.visit_short_and_long_option(x)
        raise TypeError('Not an instance of %s: %s' % (str(Argument), str(x)))

    def __call__(self, x: Argument):
        return self.visit(x)

    def visit_constant(self, x: Constant):
        raise NotImplementedError()

    def visit_named(self, x: Named):
        raise NotImplementedError()

    def visit_option(self, x: Option):
        raise NotImplementedError()

    def visit_short_and_long_option(self, x: ShortAndLongOption):
        raise NotImplementedError()


class ArgumentUsageVisitor:
    def visit(self, x: ArgumentUsage):
        if isinstance(x, Single):
            return self.visit_single(x)
        if isinstance(x, Choice):
            return self.visit_choice(x)
        raise TypeError('Not an instance of %s: %s' % (str(ArgumentUsage), str(x)))

    def __call__(self, x: ArgumentUsage):
        return self.visit(x)

    def visit_single(self, x: Single):
        raise NotImplementedError()

    def visit_choice(self, x: Choice):
        raise NotImplementedError()


class CommandLine:
    """
    A command line made up of a sequence of arguments.

    Has an optional prefix and suffix, for display purposes
    (e.g. for displaying a program name in front of the arguments).
    """

    def __init__(self,
                 argument_usages: Sequence[ArgumentUsage],
                 prefix: str = '',
                 suffix: str = ''):
        self._argument_usages = argument_usages
        self._prefix = prefix
        self._suffix = suffix

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def argument_usages(self) -> Sequence[ArgumentUsage]:
        return self._argument_usages

    def __str__(self):
        return '{}(argument_usages={}, prefix={}, suffix={})'.format(type(self),
                                                                     repr(self._argument_usages),
                                                                     repr(self._prefix),
                                                                     repr(self._suffix))


def single_mandatory(argument: Argument) -> ArgumentUsage:
    return Single(Multiplicity.MANDATORY, argument)
