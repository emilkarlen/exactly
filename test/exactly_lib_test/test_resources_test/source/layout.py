import unittest

from exactly_lib_test.test_resources.source import layout as sut
from exactly_lib_test.test_resources.source.layout import LayoutSpec


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestOptionalNewLine(),
        TestDefaultLayoutSpec(),
        TestAlternativeLayoutSpec(),
    ])


class TestOptionalNewLine(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        opt_new_line = ['the', 'optional', 'new', 'line']
        layout_spec = LayoutSpec(optional_new_line=opt_new_line)
        # ACT #
        actual = sut.OPTIONAL_NEW_LINE.layout(layout_spec)
        # ASSERT #
        self.assertEqual(opt_new_line, actual)


class TestDefaultLayoutSpec(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        actual = sut.LayoutSpec.of_default()
        # ASSERT #
        self.assertEqual((), actual.optional_new_line,
                         'optional new line')
        self.assertEqual(True, actual.symbol_reference_as_plain_symbol_name,
                         'symbol_reference_as_plain_symbol_name')
        self.assertEqual(' ', actual.token_separator,
                         'token_separator')


class TestAlternativeLayoutSpec(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        actual = sut.LayoutSpec.of_alternative()
        # ASSERT #
        self.assertEqual(('\n',), actual.optional_new_line,
                         'optional new line')
        self.assertEqual(False, actual.symbol_reference_as_plain_symbol_name,
                         'symbol_reference_as_plain_symbol_name')
        self.assertEqual('\t', actual.token_separator,
                         'token_separator')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
