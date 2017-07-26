import unittest

from exactly_lib.test_case_utils.parse import symbol_syntax as sut
from exactly_lib.test_case_utils.parse.symbol_syntax import constant, symbol


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFragment))
    ret_val.addTest(TestSplit())
    return ret_val


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
        actual = 's' == sut.Fragment('s', False)
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
