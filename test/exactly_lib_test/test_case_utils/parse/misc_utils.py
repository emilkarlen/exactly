import unittest

from exactly_lib.section_document.parser_implementations import misc_utils as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    ret_val.addTest(unittest.makeSuite(TestNewTokenStream))
    return ret_val


class TestNewTokenStream(unittest.TestCase):
    def test_pass_when_valid_syntax(self):
        source = 'token1 token2'
        actual = sut.new_token_stream(source)
        self.assertEqual(source,
                         actual.source,
                         'source string')
        self.assertEqual('token1',
                         actual.head.source_string,
                         'source string')

        # def test_raise_invalid_argument_exception_WHEN_first_token_is_invalid(self):
        #     cases = [
        #         (
        #             'start of first token is invalid',
        #             '"token1 token2'
        #         ),
        #         (
        #             'end of first token is invalid',
        #             'token1" token2'
        #         ),
        #     ]
        #     for name, source in cases:
        #         with self.subTest(name=name):
        #             with self.assertRaises(SingleInstructionInvalidArgumentException):
        #                 sut.new_token_stream(source)


class TestCases(unittest.TestCase):
    def test_fail_when_quoting_is_invalid(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.split_arguments_list_string('"a')

    def test_no_quoting(self):
        actual = sut.split_arguments_list_string('a abc abc-def abc_def')
        self.assertEqual(['a', 'abc', 'abc-def', 'abc_def'],
                         actual)

    def test_quoting(self):
        actual = sut.split_arguments_list_string('"in double quotes" ' + "'in single quotes'")
        self.assertEqual(['in double quotes', 'in single quotes'],
                         actual)


if __name__ == '__main__':
    unittest.main()
