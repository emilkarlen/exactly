import sys
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils import executable_file as sut
from shellcheck_lib.instructions.utils.parse_utils import TokenStream
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION, REL_CWD_OPTION
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.util.file_structure import DirContents, executable_file, empty_file


class TestParseValidSyntax(unittest.TestCase):
    def test_absolute_path(self):
        (ef, remaining_arguments) = sut.parse(TokenStream(sys.executable))
        self.assertEqual(sys.executable,
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(remaining_arguments.is_null)

    def test_without_option(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('file arg2'))
        self.assertEqual('file',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertEqual('arg2',
                         remaining_arguments.source)

    def test_option_without_tail(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('%s THE_FILE' % REL_HOME_OPTION))
        self.assertEqual('THE_FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(remaining_arguments.is_null)

    def test_option_with_tail(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('%s FILE tail' % REL_CWD_OPTION))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertEqual('tail',
                         remaining_arguments.source)


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream(REL_HOME_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream('--invalid-option FILE'))


class TestRelHome(unittest.TestCase):
    def test_existing_file(self):
        arguments_str = '{} file.exe remaining args'.format(REL_HOME_OPTION)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([executable_file('file.exe')])) as home_and_eds:
            self.assertEqual(str(home_and_eds.home_dir_path / 'file.exe'),
                             exe_file.path_string(home_and_eds),
                             'Path string')
            self.assertIsNone(exe_file.validator.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation pre EDS')
            self.assertIsNone(exe_file.validator.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNone(exe_file.validator.validate_pre_or_post_eds(home_and_eds),
                              'Validation pre or post EDS')

    def test_non_existing_file(self):
        arguments_str = '{} file.exe remaining args'.format(REL_HOME_OPTION)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([])) as home_and_eds:
            self.assertEqual(str(home_and_eds.home_dir_path / 'file.exe'),
                             exe_file.path_string(home_and_eds),
                             'Path string')
            self.assertIsNotNone(exe_file.validator.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                                 'Validation pre EDS')
            self.assertIsNone(exe_file.validator.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNotNone(exe_file.validator.validate_pre_or_post_eds(home_and_eds),
                                 'Validation pre or post EDS')

    def test_existing_but_non_executable_file(self):
        arguments_str = '{} file.exe remaining args'.format(REL_HOME_OPTION)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.exe')])) as home_and_eds:
            self.assertIsNotNone(exe_file.validator.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                                 'Validation pre EDS')
            self.assertIsNone(exe_file.validator.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNotNone(exe_file.validator.validate_pre_or_post_eds(home_and_eds),
                                 'Validation pre or post EDS')


class TestAbsolutePath(unittest.TestCase):
    def test_existing_file(self):
        arguments_str = py_exe.command_line_for_arguments(['remaining', 'args'])
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([])) as home_and_eds:
            self.assertEqual(sys.executable,
                             exe_file.path_string(home_and_eds),
                             'Path string')
            self.assertIsNone(exe_file.validator.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation pre EDS')
            self.assertIsNone(exe_file.validator.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNone(exe_file.validator.validate_pre_or_post_eds(home_and_eds),
                              'Validation pre or post EDS')

    def test_non_existing_file(self):
        non_existing_file = '/this/file/is/assumed/to/not/exist'
        arguments_str = '{} remaining args'.format(non_existing_file)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([])) as home_and_eds:
            self.assertEqual(non_existing_file,
                             exe_file.path_string(home_and_eds),
                             'Path string')
            self.assertIsNotNone(exe_file.validator.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                                 'Validation pre EDS')
            self.assertIsNone(exe_file.validator.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNotNone(exe_file.validator.validate_pre_or_post_eds(home_and_eds),
                                 'Validation pre or post EDS')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestAbsolutePath))
    ret_val.addTest(unittest.makeSuite(TestRelHome))
    return ret_val


if __name__ == '__main__':
    unittest.main()
