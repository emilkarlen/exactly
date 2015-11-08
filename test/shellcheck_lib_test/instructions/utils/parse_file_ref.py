import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils import parse_file_ref as sut
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents, tmp_user_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.util.file_structure import DirContents, empty_file


class TestParse(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException) as context:
            sut.parse_non_act_generated_file([])

    def test_parse_without_option(self):
        (file_ref, remaining_arguments) = sut.parse_non_act_generated_file(['FILE NAME', 'arg2'])
        self.assertEquals('FILE NAME',
                          file_ref.file_name)
        self.assertEquals(['arg2'],
                          remaining_arguments)

    def test_parse_with_option(self):
        (file_ref, remaining_arguments) = sut.parse_non_act_generated_file(['--rel-cwd', 'FILE NAME', 'arg3', 'arg4'])
        self.assertEquals('FILE NAME',
                          file_ref.file_name)
        self.assertEquals(['arg3', 'arg4'],
                          remaining_arguments)

    def test_fail_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException) as context:
            sut.parse_non_act_generated_file(['--rel-cwd'])


class TestParsesCorrectValue(unittest.TestCase):
    def test_rel_home(self):
        (file_reference, _) = sut.parse_non_act_generated_file(['--rel-home', 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_post_eds(home_and_eds).exists())

    def test_rel_cwd(self):
        (file_reference, _) = sut.parse_non_act_generated_file(['--rel-cwd', 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path_post_eds(home_and_eds).exists())

    def test_rel_tmp(self):
        (file_reference, _) = sut.parse_non_act_generated_file(['--rel-tmp', 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path_post_eds(home_and_eds).exists())

    def test_rel_home_is_default(self):
        (file_reference, _) = sut.parse_non_act_generated_file(['file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_post_eds(home_and_eds).exists())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValue))
    return ret_val


if __name__ == '__main__':
    unittest.main()
