import unittest

from exactly_lib.instructions.utils.arg_parse import parse_utils as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


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
