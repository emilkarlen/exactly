import unittest
from typing import List

from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.render import cli_program_syntax as sut
from exactly_lib_test.test_resources.test_utils import NIE


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(ArgumentOnCommandLineRendererTest),
        unittest.makeSuite(ArgumentUsageOnCommandLineRendererForMandatoryArgumentTest),
        unittest.makeSuite(ArgumentUsageOnCommandLineRendererForOptionalArgumentTest),
        unittest.makeSuite(ArgumentUsageOnCommandLineRendererForZeroOrMoreArgumentTest),
    ])


class ArgumentUsageOnCommandLineRendererForMandatoryArgumentTest(unittest.TestCase):
    def test_single(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Single(arg.Multiplicity.MANDATORY,
                                    arg.Named('name'))
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('name',
                         actual)

    def test_choice__single_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice.of_single_argument_choices(
            arg.Multiplicity.MANDATORY,
            [arg.Named('name1'), arg.Named('name2')],
        )
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('(name1|name2)',
                         actual)

    def test_choice__multiple_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        for choices_case in _CHOICE_MULTIPLE_CHOICE_ARGUMENTS_CASES:
            with self.subTest(choices_case.name):
                argument_usage = _choice_w_multiple_args_from_strings(
                    arg.Multiplicity.MANDATORY,
                    choices_case.input_value,
                )
                # ACT #
                actual = renderer.visit(argument_usage)
                # ASSERT #
                expected = _mandatory__choice(choices_case.expected_value)
                self.assertEqual(expected,
                                 actual)


class ArgumentUsageOnCommandLineRendererForOptionalArgumentTest(unittest.TestCase):
    def test_single(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Single(arg.Multiplicity.OPTIONAL,
                                    arg.Named('name'))
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('[name]',
                         actual)

    def test_choice__single_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice.of_single_argument_choices(
            arg.Multiplicity.OPTIONAL,
            [arg.Named('name1'), arg.Named('name2')],
        )
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('[name1|name2]',
                         actual)

    def test_choice__multiple_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        for choices_case in _CHOICE_MULTIPLE_CHOICE_ARGUMENTS_CASES:
            with self.subTest(choices_case.name):
                argument_usage = _choice_w_multiple_args_from_strings(
                    arg.Multiplicity.OPTIONAL,
                    choices_case.input_value,
                )
                # ACT #
                actual = renderer.visit(argument_usage)
                # ASSERT #
                expected = _optional__choice(choices_case.expected_value)
                self.assertEqual(expected,
                                 actual)


class ArgumentUsageOnCommandLineRendererForZeroOrMoreArgumentTest(unittest.TestCase):
    def test_single(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                                    arg.Named('name'))
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('[name]...',
                         actual)

    def test_choice__single_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice.of_single_argument_choices(
            arg.Multiplicity.ZERO_OR_MORE,
            [arg.Named('name1'), arg.Named('name2')],
        )
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('[name1|name2]...',
                         actual)

    def test_choice__multiple_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        for choices_case in _CHOICE_MULTIPLE_CHOICE_ARGUMENTS_CASES:
            with self.subTest(choices_case.name):
                argument_usage = _choice_w_multiple_args_from_strings(
                    arg.Multiplicity.ONE_OR_MORE,
                    choices_case.input_value,
                )
                # ACT #
                actual = renderer.visit(argument_usage)
                # ASSERT #
                expected = _one_or_more__choice(choices_case.expected_value)
                self.assertEqual(expected,
                                 actual)


class ArgumentUsageOnCommandLineRendererForOneOrMoreArgumentTest(unittest.TestCase):
    def test_single(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Single(arg.Multiplicity.ONE_OR_MORE,
                                    arg.Named('name'))
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('name...',
                         actual)

    def test_choice__single_argument_choices(self):
        # ARRANGE #
        args_cases = [
            ['name1', 'name2'],
            ['name1', 'name2', 'name3'],
        ]
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        for args_case in args_cases:
            with self.subTest(repr(args_case)):
                argument_usage = arg.Choice.of_single_argument_choices(
                    arg.Multiplicity.ONE_OR_MORE,
                    [arg.Named(arg_name) for arg_name in args_case],
                )
                # ACT #
                actual = renderer.visit(argument_usage)
                # ASSERT #
                self.assertEqual('({})...'.format('|'.join(args_case)),
                                 actual)

    def test_choice__multiple_argument_choices(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        for choices_case in _CHOICE_MULTIPLE_CHOICE_ARGUMENTS_CASES:
            with self.subTest(choices_case.name):
                argument_usage = _choice_w_multiple_args_from_strings(
                    arg.Multiplicity.ONE_OR_MORE,
                    choices_case.input_value,
                )
                # ACT #
                actual = renderer.visit(argument_usage)
                # ASSERT #
                expected = _one_or_more__choice(choices_case.expected_value)
                self.assertEqual(expected,
                                 actual)


class ArgumentOnCommandLineRendererTest(unittest.TestCase):
    def test_option(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.option('long')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('-long',
                         actual)

    def test_option_only_short_name_SHOULD_produce_short_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.short_long_option(short_name='s')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('-s',
                         actual)

    def test_option_only_long_name_SHOULD_produce_long_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.short_long_option(long_name='long')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('--long',
                         actual)

    def test_option_with_both_long_and_short_name_SHOULD_produce_short_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.short_long_option(short_name='s',
                                               long_name='long')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('-s',
                         actual)

    def test_named_argument_SHOULD_produce_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.Named('the_name')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('the_name',
                         actual)

    def test_constant_argument_should_produce_constant_string(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.Constant('the_constant')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('the_constant',
                         actual)


def _mandatory__choice(choice: str) -> str:
    return '({})'.format(choice)


def _optional__choice(choice: str) -> str:
    return '[{}]'.format(choice)


def _zero_or_more__choice(choice: str) -> str:
    return '[{}]...'.format(choice)


def _one_or_more__choice(choice: str) -> str:
    return '({})...'.format(choice)


def _choice_w_multiple_args_from_strings(multiplicity: arg.Multiplicity,
                                         choices: List[List[str]],
                                         ) -> arg.Choice:
    return arg.Choice.of_multiple_argument_choices(
        multiplicity,
        [
            [arg.Named(choice_arg) for choice_arg in choice]
            for choice in choices
        ]
    )


_CHOICE_MULTIPLE_CHOICE_ARGUMENTS_CASES = [
    NIE(
        'two arguments',
        input_value=[['a1', 'a2'], ['b1', 'b2']],
        expected_value='|'.join(['a1 a2', 'b1 b2'])
    ),
    NIE(
        'mixed number of arguments',
        input_value=[['a'], ['b1', 'b2'], ['c1', 'c2', 'c3']],
        expected_value='|'.join(['a', 'b1 b2', 'c1 c2 c3'])
    ),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
