import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException

from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib.instructions.setup import install as sut
from shellcheck_lib_test.util import file_structure


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = utils.new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = utils.new_source('instruction-name', 'argument1 argument2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        source = utils.new_source('instruction-name', 'single-argument')
        sut.Parser().apply(source)

    def test_argument_shall_be_parsed_using_shell_syntax(self):
        source = utils.new_source('instruction-name', "'this is a single argument'")
        sut.Parser().apply(source)


class TestValidationErrorScenarios(TestCaseBase):
    def test_HARD_ERROR_when_file_does_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 expected_pre_validation_result=svh_check.is_validation_error(),
                 ),
            utils.new_source('instruction-name',
                             'source-that-do-not-exist'))


class TestSuccessfulScenarios(TestCaseBase):
    def test_install_file(self):
        file_name = 'existing-file'
        file_to_install = file_structure.File(file_name,
                                              'contents')
        expected_act_contents = file_structure.DirContents([file_to_install])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=file_structure.DirContents([file_to_install]),
                 expected_main_side_effects_on_files=eds_contents_check.ActRootContainsExactly(
                     expected_act_contents)
                 ),
            utils.new_source('instruction-name',
                             file_name))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestValidationErrorScenarios))
    return ret_val


if __name__ == '__main__':
    unittest.main()
