import pathlib
import tempfile
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils import parse_file_ref as sut
from shellcheck_lib.instructions.utils.parse_utils import TokenStream
from shellcheck_lib.instructions.utils.relative_path_options import REL_CWD_OPTION, REL_HOME_OPTION, REL_TMP_OPTION
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents, tmp_user_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.test_resources.file_structure import DirContents, empty_file


class TestParse(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_relative_file_argument([])

    def test_parse_without_option(self):
        (file_ref, remaining_arguments) = sut.parse_relative_file_argument(['FILE NAME', 'arg2'])
        self.assertEquals('FILE NAME',
                          file_ref.file_name)
        self.assertEquals(['arg2'],
                          remaining_arguments)

    def test_parse_with_option(self):
        (file_ref, remaining_arguments) = sut.parse_relative_file_argument(
            [REL_CWD_OPTION, 'FILE NAME', 'arg3', 'arg4'])
        self.assertEquals('FILE NAME',
                          file_ref.file_name)
        self.assertEquals(['arg3', 'arg4'],
                          remaining_arguments)

    def test_fail_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_relative_file_argument([REL_CWD_OPTION])


class TestParsesCorrectValue(unittest.TestCase):
    def test_rel_home(self):
        (file_reference, _) = sut.parse_relative_file_argument([REL_HOME_OPTION, 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())

    def test_rel_cwd(self):
        (file_reference, _) = sut.parse_relative_file_argument([REL_CWD_OPTION, 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())

    def test_rel_tmp(self):
        (file_reference, _) = sut.parse_relative_file_argument([REL_TMP_OPTION, 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())

    def test_absolute(self):
        abs_path_str = str(pathlib.Path.cwd().resolve())
        (file_reference, _) = sut.parse_relative_file_argument([abs_path_str])
        with tempfile.TemporaryDirectory(prefix="shellcheck-home-") as home_dir:
            home_dir_path = pathlib.Path(home_dir)
            self.assertTrue(file_reference.file_path_pre_eds(home_dir_path).exists())

    def test_rel_home_is_default(self):
        (file_reference, _) = sut.parse_relative_file_argument(['file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())


class TestParseFromTokenStream(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream(None))

    def test_parse_without_option(self):
        (file_ref, remaining_arguments) = sut.parse_file_ref(TokenStream('FILENAME arg2'))
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        self.assertEquals('arg2',
                          remaining_arguments.source)

    def test_parse_with_option(self):
        (file_ref, remaining_arguments) = sut.parse_file_ref(
            TokenStream(REL_CWD_OPTION + ' FILENAME arg3 arg4'))
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        self.assertEquals('arg3 arg4',
                          remaining_arguments.source)

    def test_fail_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream(REL_CWD_OPTION))


class TestParsesCorrectValueFromTokenStream(unittest.TestCase):
    def test_rel_home(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('%s file.txt' % REL_HOME_OPTION))
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())

    def test_rel_cwd(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('%s file.txt' % REL_CWD_OPTION))
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())

    def test_rel_tmp(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('%s file.txt' % REL_TMP_OPTION))
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())

    def test_absolute(self):
        abs_path_str = str(pathlib.Path.cwd().resolve())
        (file_reference, _) = sut.parse_file_ref(TokenStream(abs_path_str))
        with tempfile.TemporaryDirectory(prefix="shellcheck-home-") as home_dir:
            home_dir_path = pathlib.Path(home_dir)
            self.assertTrue(file_reference.file_path_pre_eds(home_dir_path).exists())

    def test_rel_home_is_default(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('file.txt'))
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_eds).exists())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValue))
    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromTokenStream))
    return ret_val


if __name__ == '__main__':
    unittest.main()
