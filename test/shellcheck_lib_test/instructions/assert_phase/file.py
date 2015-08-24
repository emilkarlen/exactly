import unittest

from shellcheck_lib.instructions.assert_phase import file
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.assert_phase.utils import AssertInstructionTest, new_source, new_line_sequence
from shellcheck_lib_test.util.file_structure import DirContents, empty_file, empty_dir, File, Link

syntax_list = [
    ('FILENAME', 'File exists as any type of file (regular, directory, ...)'),
    ('FILENAME type [regular|directory]', 'File exists and has given type'),
    ('FILENAME empty', 'File exists, is a regular file, and is empty'),
    ('FILENAME ! empty', 'File exists, is a regular file, and is not empty'),
]


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

    def test_link_fail__when__file_exists_and_is_regular_file(self):
        file_name = 'name-of-existing-file'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_file(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' type symlink'))

    def test_link_fail__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_dir(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' type symlink'))

    def test_pass__when__file_type_is_given__link_to_directory(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_dir('dir'),
                                                                             Link('link-file', 'dir')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'link-file type symlink'))

    def test_pass__when__file_type_is_given__link_to_regular_file(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_file('file'),
                                                                             Link('link-file', 'file')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'link-file type symlink'))


class TestFileContentsEmptyInvalidSyntax(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name empty superfluous-argument'
        parser = file.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name ' + arguments),
                          arguments)


class TestFileContentsEmptyValidSyntax(unittest.TestCase):
    def test_fail__when__file_do_not_exist(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult())
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'name-of-non-existing-file empty'))

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_dir(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' empty'))

    def test_fail__when__file_exists_but_is_non_empty(self):
        file_name = 'name-of-existing-file'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([File(file_name, 'contents')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' empty'))

    def test_pass__when__file_exists_and_is_empty(self):
        file_name = 'name-of-existing-file'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_file(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' empty'))


class TestFileContentsNonEmptyInvalidSyntax(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name ! empty superfluous-argument'
        parser = file.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name ' + arguments),
                          arguments)


class TestFileContentsNonEmptyValidSyntax(unittest.TestCase):
    def test_fail__when__file_do_not_exist(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult())
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'name-of-non-existing-file ! empty'))

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_dir(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' ! empty'))

    def test_fail__when__file_exists_but_is_empty(self):
        file_name = 'name-of-existing-file'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([empty_file(file_name)]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' ! empty'))

    def test_pass__when__file_exists_and_is_non_empty(self):
        file_name = 'name-of-existing-file'
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     act_dir_contents_after_act=DirContents([File(file_name, 'contents')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', file_name + ' ! empty'))


class TestFileContentsFileFailureBeforeComparingContents(unittest.TestCase):
    def test_validation_error__when__comparison_file_does_not_exist(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     home_dir_contents=DirContents([empty_file('f')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'name-of-non-existing-file contents --rel-home f.txt'))

    def test_validation_error__when__comparison_file_is_a_directory(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     home_dir_contents=DirContents([empty_dir('dir')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'name-of-non-existing-file contents --rel-home dir'))

    def test_fail__when__target_file_does_not_exist(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     home_dir_contents=DirContents([empty_file('f.txt')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'name-of-non-existing-file contents --rel-home f.txt'))

    def test_fail__when__target_file_is_a_directory(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     home_dir_contents=DirContents([empty_file('f.txt')]),
                                     act_dir_contents_after_act=DirContents([empty_dir('dir')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'dir contents --rel-home f.txt'))


class TestFileContentsFileComparisons(unittest.TestCase):
    def test_fail__when__contents_differ(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(),
                                     home_dir_contents=DirContents([empty_file('f.txt')]),
                                     act_dir_contents_after_act=DirContents([File('target.txt', 'non-empty')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'target.txt contents --rel-home f.txt'))

    def test_pass__when__contents_equals(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(),
                                     home_dir_contents=DirContents([File('f.txt', 'contents')]),
                                     act_dir_contents_after_act=DirContents([File('target.txt', 'contents')]))
        test.apply(self,
                   file.Parser(),
                   new_source('instruction-name', 'target.txt contents --rel-home f.txt'))

def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestFileTypeAndExistence))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileFailureBeforeComparingContents))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileComparisons))
    return ret_val


if __name__ == '__main__':
    unittest.main()
