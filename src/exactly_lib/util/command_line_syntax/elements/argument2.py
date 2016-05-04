import unittest
from enum import Enum


class SyntaxElement:
    def __init__(self,
                 name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class ArgumentValueElement:
    def __init__(self, str_or_syntax_element):
        self.str_or_syntax_element = str_or_syntax_element

    @property
    def is_str(self) -> bool:
        return isinstance(self.str_or_syntax_element, str)

    @property
    def is_syntax_element(self) -> bool:
        return isinstance(self.str_or_syntax_element, SyntaxElement)

    @property
    def str_value(self) -> str:
        """
        Precondition: `self.is_str`
        """
        return self.str_or_syntax_element

    @property
    def syntax_element_value(self) -> SyntaxElement:
        """
        Precondition: `self.is_syntax_element`
        """
        return self.str_or_syntax_element


class Argument:
    pass


class Constant(Argument):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Named(Argument):
    def __init__(self,
                 element: ArgumentValueElement):
        self._element = element

    @property
    def element(self) -> ArgumentValueElement:
        return self._element


class Option(Argument):
    def __init__(self,
                 short_name: str = '',
                 long_name: str = '',
                 element: ArgumentValueElement = None):
        self._short_name = short_name
        self._long_name = long_name
        self._element = element

    @property
    def short_name(self) -> str:
        return self._short_name

    @property
    def long_name(self) -> str:
        return self._long_name

    @property
    def element(self) -> ArgumentValueElement:
        """

        :return: `None` if option does not have an argument.
        """
        return self._element


class Multiplicity(Enum):
    OPTIONAL = 1
    MANDATORY = 2


class ArgumentUsage:
    """
    How one or more `Argument`s are used.
    """

    def __init__(self,
                 usage_type: Multiplicity):
        self._usage_type = usage_type

    @property
    def multiplicity(self) -> Multiplicity:
        return self._usage_type


class Single(ArgumentUsage):
    """
    A single `Argument`
    """

    def __init__(self,
                 usage_type: Multiplicity,
                 argument: Argument):
        super().__init__(usage_type)
        self._argument = argument

    @property
    def argument(self) -> Argument:
        return self._argument


class Choice(ArgumentUsage):
    """
    A choice between two or more `Argument`s.
    """

    def __init__(self,
                 usage_type: Multiplicity,
                 arguments: list):
        """
        :type arguments: [`Argument`]
        """
        super().__init__(usage_type)
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
    def __init__(self,
                 program_name: str,
                 argument_usages: list):
        self._program_name = program_name
        self._argument_usages = argument_usages

    @property
    def program_name(self) -> str:
        return self._program_name

    @property
    def argument_usages(self) -> list:
        """
        :rtype: [`ArgumentUsage`]
        """
        return self._argument_usages


class ArgumentRecordingArgumentVisitor(ArgumentVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_constant(self, x: Constant):
        self.visited_classes.append(Constant)
        return x

    def visit_named(self, x: Named):
        self.visited_classes.append(Named)
        return x

    def visit_option(self, x: Option):
        self.visited_classes.append(Option)
        return x


class ArgumentVisitorTest(unittest.TestCase):
    def test_as_is(self):
        self._check(Constant('name'), Constant)

    def test_positional(self):
        self._check(Named(ArgumentValueElement('value-element')), Named)

    def test_plain_option(self):
        self._check(Option('n'), Option)

    def test_visit_SHOULD_raise_TypeError_WHEN_argument_is_not_a_sub_class_of_argument(self):
        visitor = ArgumentRecordingArgumentVisitor()
        with self.assertRaises(TypeError):
            visitor.visit('not an argument')

    def _check(self, x: Argument, expected_class):
        # ARRANGE #
        visitor = ArgumentRecordingArgumentVisitor()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertListEqual([expected_class],
                             visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'Visitor should return the return-value of the visited method')
