import unittest

from shellcheck_lib.instructions.assert_phase import file
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.assert_phase.utils import AssertInstructionTest, new_source, new_line_sequence
from shellcheck_lib_test.util.file_structure import DirContents, empty_file, empty_dir


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = file.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name '),
                          '')


class TestFileTypeAndExistence(unittest.TestCase):
    def test_fail__when__file_do_not_exist(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult())
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'name-of-non-existing-file'))

    def test_pass__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_dir(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name))

    def test_pass__when__file_exists_and_is_regular_file(self):
        file_name = 'name-of-existing-file'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_file(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name))

    def test_pass__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_dir(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' type directory'))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestFileTypeAndExistence))
    return ret_val


if __name__ == '__main__':
    unittest.main()
