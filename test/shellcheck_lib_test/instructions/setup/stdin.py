import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.setup import stdin as sut
from shellcheck_lib_test.instructions.test_resources.utils import new_source


class TestParseSet(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_three_argument(self):
        source = new_source('instruction-name', '--rel-home file superfluous-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_home(self):
        source = new_source('instruction-name', '--rel-home file')
        sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_cwd(self):
        source = new_source('instruction-name', '--rel-cwd file')
        sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_tmp(self):
        source = new_source('instruction-name', '--rel-tmp file')
        sut.Parser().apply(source)

    def test_file_name_can_be_quoted(self):
        source = new_source('instruction-name', '--rel-home "file name with space"')
        sut.Parser().apply(source)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseSet))
    return ret_val


if __name__ == '__main__':
    unittest.main()
