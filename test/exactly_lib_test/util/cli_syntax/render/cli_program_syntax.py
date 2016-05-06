import unittest

from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.render import cli_program_syntax as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(ArgumentOnCommandLineRendererTest),
        unittest.makeSuite(ArgumentUsageOnCommandLineRendererForMandatoryArgumentTest),
        unittest.makeSuite(ArgumentUsageOnCommandLineRendererForOptionalArgumentTest),
        unittest.makeSuite(ArgumentUsageOnCommandLineRendererForZeroOrMoreArgumentTest),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


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

    def test_choice(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice(arg.Multiplicity.MANDATORY,
                                    [arg.Named('name1'), arg.Named('name2')])
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('(name1|name2)',
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

    def test_choice(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice(arg.Multiplicity.OPTIONAL,
                                    [arg.Named('name1'), arg.Named('name2')])
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('[name1|name2]',
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

    def test_choice(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice(arg.Multiplicity.ZERO_OR_MORE,
                                    [arg.Named('name1'), arg.Named('name2')])
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('[name1|name2]...',
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

    def test_choice(self):
        # ARRANGE #
        renderer = sut.ArgumentUsageOnCommandLineRenderer()
        argument_usage = arg.Choice(arg.Multiplicity.ONE_OR_MORE,
                                    [arg.Named('name1'), arg.Named('name2')])
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('(name1|name2)...',
                         actual)


class ArgumentOnCommandLineRendererTest(unittest.TestCase):
    def test_option_with_both_long_and_short_name_SHOULD_produce_short_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.option(short_name='s',
                                    long_name='long')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('-s',
                         actual)

    def test_option_only_short_name_SHOULD_produce_short_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.option(short_name='s')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('-s',
                         actual)

    def test_option_only_long_name_SHOULD_produce_long_name(self):
        # ARRANGE #
        renderer = sut.ArgumentOnCommandLineRenderer()
        argument_usage = arg.option(long_name='long')
        # ACT #
        actual = renderer.visit(argument_usage)
        # ASSERT #
        self.assertEqual('--long',
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
