import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib.instructions.setup import install as sut


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = utils.new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source.line_sequence)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = utils.new_source('instruction-name', 'argument1 argument2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source.line_sequence)

    def test_succeed_when_there_is_exactly_one_argument(self):
        source = utils.new_source('instruction-name', 'single-argument')
        sut.Parser().apply(source.line_sequence)

    def test_argument_shall_be_parsed_using_shell_syntax(self):
        source = utils.new_source('instruction-name', "'this is a single argument'")
        sut.Parser().apply(source.line_sequence)


class TestSourceMustBeAnExistingFileRelativeTheHomeDirectory(TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(sut.Parser(),
                 expected_pre_validation_result=svh_check.is_validation_error(),
                 ),
            utils.new_source('instruction-name',
                             'source-that-do-not-exist'))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestSourceMustBeAnExistingFileRelativeTheHomeDirectory))
    return ret_val


if __name__ == '__main__':
    unittest.main()
