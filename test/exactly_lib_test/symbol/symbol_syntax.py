import unittest

from exactly_lib.symbol import symbol_syntax as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME, NOT_A_VALID_SYMBOL_NAME


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSymbolReference),
        unittest.makeSuite(TestParseMaybeSymbolReference),
    ])


class TestParseSymbolReference(unittest.TestCase):
    def test_None_WHEN_not_surrounded_by_symbol_reference_markers(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'no markers at all - valid symbol name',
                A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'no markers at all - invalid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'markers at beginning, only',
                sut.SYMBOL_REFERENCE_BEGIN + A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'markers at end, only',
                A_VALID_SYMBOL_NAME + sut.SYMBOL_REFERENCE_END,
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = sut.parse_symbol_reference__from_str(case.value)
                # ASSERT #
                self.assertIsNone(actual)

    def test_Exception_WHEN_invalid_symbol_name_surrounded_by_symbol_reference_markers(self):
        with self.assertRaises(sut.SingleInstructionInvalidArgumentException):
            sut.parse_symbol_reference__from_str(
                sut.symbol_reference_syntax_for_name(NOT_A_VALID_SYMBOL_NAME)
            )

    def test_name_of_symbol_WHEN_valid_symbol_name_surrounded_by_symbol_reference_markers(self):
        # ACT #
        actual = sut.parse_symbol_reference__from_str(
            sut.symbol_reference_syntax_for_name(A_VALID_SYMBOL_NAME)
        )
        # ASSERT #
        self.assertEqual(A_VALID_SYMBOL_NAME, actual)


class TestParseMaybeSymbolReference(unittest.TestCase):
    def test_None_WHEN_not_surrounded_by_symbol_reference_markers_or_not_a_valid_symbol_name(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'no markers at all - valid symbol name',
                A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'no markers at all - invalid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'markers at beginning, only',
                sut.SYMBOL_REFERENCE_BEGIN + A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'markers at end, only',
                A_VALID_SYMBOL_NAME + sut.SYMBOL_REFERENCE_BEGIN,
            ),
            NameAndValue(
                'markers at end, only',
                A_VALID_SYMBOL_NAME + sut.SYMBOL_REFERENCE_END,
            ),
            NameAndValue(
                'invalid symbol name',
                sut.symbol_reference_syntax_for_name(NOT_A_VALID_SYMBOL_NAME),
            ),
            NameAndValue(
                'two consecutive symbol references',
                (sut.symbol_reference_syntax_for_name(A_VALID_SYMBOL_NAME) +
                 sut.symbol_reference_syntax_for_name(A_VALID_SYMBOL_NAME)),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = sut.parse_maybe_symbol_reference(case.value)
                # ASSERT #
                self.assertIsNone(actual)

    def test_name_of_symbol_WHEN_valid_symbol_name_surrounded_by_symbol_reference_markers(self):
        # ACT #
        actual = sut.parse_maybe_symbol_reference(
            sut.symbol_reference_syntax_for_name(A_VALID_SYMBOL_NAME)
        )
        # ASSERT #
        self.assertEqual(A_VALID_SYMBOL_NAME, actual)
