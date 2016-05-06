from enum import Enum


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


class Option(Argument):
    """
    A traditional command line option.
    """

    def __init__(self,
                 short_name: str = '',
                 long_name: str = '',
                 argument: str = ''):
        self._short_name = short_name
        self._long_name = long_name
        self._argument = argument

    @property
    def short_name(self) -> str:
        return self._short_name

    @property
    def long_name(self) -> str:
        return self._long_name

    @property
    def argument(self) -> str:
        """
        :return: Empty `str` if option does not have an argument.
        """
        return self._argument


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


class Choice(ArgumentUsage):
    """
    A choice between two or more `Argument`s.
    """

    def __init__(self,
                 multiplicity: Multiplicity,
                 arguments: list):
        """
        :type arguments: [`Argument`]
        """
        super().__init__(multiplicity)
        self._arguments = arguments

    @property
    def arguments(self) -> list:
        """
        :rtype: [`Argument`]
        """
        return self._arguments


class ArgumentVisitor:
    def visit(self, x: Argument):
        if isinstance(x, Constant):
            return self.visit_constant(x)
        if isinstance(x, Named):
            return self.visit_named(x)
        if isinstance(x, Option):
            return self.visit_option(x)
        raise TypeError('Not an instance of %s: %s' % (str(Argument), str(x)))

    def __call__(self, x: Argument):
        return self.visit(x)

    def visit_constant(self, x: Constant):
        raise NotImplementedError()

    def visit_named(self, x: Named):
        raise NotImplementedError()

    def visit_option(self, x: Option):
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
                 argument_usages: list,
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
    def argument_usages(self) -> list:
        """
        :rtype: [`ArgumentUsage`]
        """
        return self._argument_usages
