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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
