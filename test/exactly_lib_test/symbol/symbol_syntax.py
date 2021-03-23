import unittest

from exactly_lib.symbol import symbol_syntax as sut
from exactly_lib.symbol.symbol_syntax import constant, symbol
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME, NOT_A_VALID_SYMBOL_NAME


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFragment),
        TestSplit(),
        unittest.makeSuite(TestParseSymbolReference),
        unittest.makeSuite(TestParseMaybeSymbolReference),
    ])


class TestFragment(unittest.TestCase):
    def test_equals_fragment(self):
        for s1 in ['a', 'b']:
            for s2 in ['a', 'b']:
                for b1 in [False, True]:
                    for b2 in [False, True]:
                        with self.subTest(s1=s1, s2=s2, b1=b1, b2=b2):
                            v1 = sut.Fragment(s1, b1)
                            v2 = sut.Fragment(s2, b2)
                            actual = v1 == v2
                            expected = s1 == s2 and b1 == b2
                            self.assertEqual(expected, actual)

    def test_equals_string(self):
        actual = 's' == sut.constant('s')
        self.assertFalse(actual)


class TestSplit(unittest.TestCase):
    def runTest(self):
        cases = [
            ('', []),
            ('abc', [constant('abc')]),
            (
                sut.symbol_reference_syntax_for_name('sym_name'),
                [symbol('sym_name')]
            ),
            (
                sut.symbol_reference_syntax_for_name('sym_NAME_1'),
                [symbol('sym_NAME_1')]
            ),
            (
                sut.symbol_reference_syntax_for_name('not a symbol name'),
                [constant(sut.symbol_reference_syntax_for_name('not a symbol name'))]
            ),
            (
                sut.symbol_reference_syntax_for_name(''),
                [constant(sut.symbol_reference_syntax_for_name(''))]
            ),
            (
                sut.symbol_reference_syntax_for_name('  '),
                [constant(sut.symbol_reference_syntax_for_name('  '))]
            ),
            (
                sut.symbol_reference_syntax_for_name('1isAValidSymbolName'),
                [symbol('1isAValidSymbolName')]
            ),
            (
                'const{sym_ref}'.format(sym_ref=sut.symbol_reference_syntax_for_name('sym_name')),
                [constant('const'),
                 symbol('sym_name')]
            ),
            (
                '{sym_ref}const'.format(sym_ref=sut.symbol_reference_syntax_for_name('sym_name')),
                [symbol('sym_name'),
                 constant('const')]
            ),
            (
                '{sym_ref1}{sym_ref2}'.format(
                    sym_ref1=sut.symbol_reference_syntax_for_name('sym_name1'),
                    sym_ref2=sut.symbol_reference_syntax_for_name('sym_name2')),
                [symbol('sym_name1'),
                 symbol('sym_name2')]
            ),
            (
                '{sym_begin}{sym_ref}'.format(
                    sym_begin=sut.SYMBOL_REFERENCE_BEGIN,
                    sym_ref=sut.symbol_reference_syntax_for_name('sym_name')),
                [constant(sut.SYMBOL_REFERENCE_BEGIN),
                 symbol('sym_name')]
            ),
            (
                '{sym_ref1}const 1{not_a_symbol_name1}{not_a_symbol_name2}const 2{sym_ref2}'.format(
                    sym_ref1=sut.symbol_reference_syntax_for_name('sym_name1'),
                    not_a_symbol_name1=sut.symbol_reference_syntax_for_name('not a sym1'),
                    not_a_symbol_name2=sut.symbol_reference_syntax_for_name('not a sym2'),
                    sym_ref2=sut.symbol_reference_syntax_for_name('sym_name2')),
                [symbol('sym_name1'),
                 constant('const 1' +
                          sut.symbol_reference_syntax_for_name('not a sym1') +
                          sut.symbol_reference_syntax_for_name('not a sym2') +
                          'const 2'),
                 symbol('sym_name2')]
            ),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                actual = sut.split(source)
                self.assertEqual(expected,
                                 actual)


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
