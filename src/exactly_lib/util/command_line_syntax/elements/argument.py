import unittest
from enum import Enum


class Argument:
    pass


class AsIsArgument(Argument):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class SyntaxElementArgument(Argument):
    def __init__(self,
                 name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class PlainOptionArgument(Argument):
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
        return self._argument


# class OptionGroup(Argument):
#     def __init__(self, name: str):
#         self._name = name
#
#     @property
#     def name(self) -> str:
#         return self._name


class PositionalArgument(tuple):
    def __new__(cls,
                name: str):
        return tuple.__new__(cls, (name,))

    @property
    def name(self) -> str:
        return self[0]


class ArgumentUsageType(Enum):
    OPTIONAL = 1
    MANDATORY = 2


class ArgumentUsage(tuple):
    def __new__(cls,
                option: Argument,
                usage_type: ArgumentUsageType):
        return tuple.__new__(cls, (option, usage_type))

    @property
    def argument(self) -> Argument:
        return self[0]

    @property
    def usage_type(self) -> ArgumentUsageType:
        return self[1]


class ArgumentVisitor:
    def visit(self, x: Argument):
        if isinstance(x, AsIsArgument):
            return self.visit_as_is(x)
        if isinstance(x, PositionalArgument):
            return self.visit_positional(x)
        if isinstance(x, PlainOptionArgument):
            return self.visit_plain_option(x)
        if isinstance(x, SyntaxElementArgument):
            return self.visit_syntax_element(x)
        raise TypeError('Not an instance of %s: %s' % (str(Argument), str(x)))

    def visit_as_is(self, x: AsIsArgument):
        raise NotImplementedError()

    def visit_positional(self, x: PositionalArgument):
        raise NotImplementedError()

    def visit_syntax_element(self, x: SyntaxElementArgument):
        raise NotImplementedError()

    def visit_plain_option(self, x: PlainOptionArgument):
        raise NotImplementedError()


class ArgumentRecordingArgumentVisitor(ArgumentVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_as_is(self, x: AsIsArgument):
        self.visited_classes.append(AsIsArgument)
        return x

    def visit_positional(self, x: PositionalArgument):
        self.visited_classes.append(PositionalArgument)
        return x

    def visit_syntax_element(self, x: SyntaxElementArgument):
        self.visited_classes.append(SyntaxElementArgument)
        return x

    def visit_plain_option(self, x: PlainOptionArgument):
        self.visited_classes.append(PlainOptionArgument)
        return x


class ArgumentVisitorTest(unittest.TestCase):
    def test_as_is(self):
        self._check(AsIsArgument('name'), AsIsArgument)

    def test_positional(self):
        self._check(PositionalArgument('name'), PositionalArgument)

    def test_plain_option(self):
        self._check(PlainOptionArgument('name'), PlainOptionArgument)

    def test_syntax_element(self):
        self._check(SyntaxElementArgument('name'), SyntaxElementArgument)

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
