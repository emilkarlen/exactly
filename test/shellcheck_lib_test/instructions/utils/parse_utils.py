import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils import parse_utils as sut


class TestCases(unittest.TestCase):
    def test_fail_when_quoting_is_invalid(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.spit_arguments_list_string('"a')

    def test_no_quoting(self):
        actual = sut.spit_arguments_list_string('a abc abc-def abc_def')
        self.assertEqual(['a', 'abc', 'abc-def', 'abc_def'],
                         actual)

    def test_quoting(self):
        actual = sut.spit_arguments_list_string('"in double quotes" ' + "'in single quotes'")
        self.assertEqual(['in double quotes', 'in single quotes'],
                         actual)


class TestTokenStream(unittest.TestCase):
    def test_should_be_null_when_source_is_none(self):
        actual = sut.TokenStream(None)
        self.assertTrue(actual.is_null)
        self.assertIsNone(actual.source)

    def test_should_be_null_when_source_is_empty_string(self):
        actual = sut.TokenStream('')
        self.assertTrue(actual.is_null)
        self.assertEquals('',
                          actual.source)

    def test_should_be_null_when_source_is_only_white_space(self):
        actual = sut.TokenStream('   ')
        self.assertTrue(actual.is_null)
        self.assertEquals('   ',
                          actual.source)

    def test_single_token(self):
        actual = sut.TokenStream('a ')
        self.assertFalse(actual.is_null)
        self.assertEqual('a',
                         actual.head)
        self.assertEqual('a ',
                         actual.source)
        self.assertIsNone(actual.tail_source)
        self.assertEquals('',
                          actual.tail_source_or_empty_string)

    def test_multiple_tokens(self):
        actual = sut.TokenStream('a b  ')
        self.assertFalse(actual.is_null)
        self.assertEqual('a',
                         actual.head)
        self.assertEqual('a b  ',
                         actual.source)
        self.assertEqual('b  ',
                         actual.tail_source)
        self.assertEqual('b  ',
                         actual.tail_source_or_empty_string)

    def test_multiple_tokens_tail(self):
        tokens0 = sut.TokenStream('a b  ')
        actual = tokens0.tail
        self.assertFalse(actual.is_null)
        self.assertEqual('b',
                         actual.head)
        self.assertEqual('b  ',
                         actual.source)
        self.assertIsNone(actual.tail_source)
        self.assertEqual('',
                         actual.tail_source_or_empty_string)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    ret_val.addTest(unittest.makeSuite(TestTokenStream))
    return ret_val


if __name__ == '__main__':
    unittest.main()
