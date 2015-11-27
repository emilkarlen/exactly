import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils import executable_file as sut
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.util.file_structure import DirContents, executable_file, empty_file


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_option_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_as_first_space_separated_part('file.exe')

    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_as_first_space_separated_part(REL_HOME_OPTION)

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_as_first_space_separated_part('--invalid-option FILE')


class TestRelHome(unittest.TestCase):
    def test_existing_file(self):
        arguments_str = '{} file.exe remaining args'.format(REL_HOME_OPTION)
        (exe_file, remaining_arguments) = sut.parse_as_first_space_separated_part(arguments_str)
        self.assertEqual('remaining args',
                         remaining_arguments,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([executable_file('file.exe')])) as home_and_eds:
            self.assertEqual(str(home_and_eds.home_dir_path / 'file.exe'),
                             exe_file.path_string(home_and_eds),
                             'Path string')
            self.assertIsNone(exe_file.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation pre EDS')
            self.assertIsNone(exe_file.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNone(exe_file.validate_pre_or_post_eds(home_and_eds),
                              'Validation pre or post EDS')

    def test_non_existing_file(self):
        arguments_str = '{} file.exe remaining args'.format(REL_HOME_OPTION)
        (exe_file, remaining_arguments) = sut.parse_as_first_space_separated_part(arguments_str)
        self.assertEqual('remaining args',
                         remaining_arguments,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([])) as home_and_eds:
            self.assertEqual(str(home_and_eds.home_dir_path / 'file.exe'),
                             exe_file.path_string(home_and_eds),
                             'Path string')
            self.assertIsNotNone(exe_file.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                                 'Validation pre EDS')
            self.assertIsNone(exe_file.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNotNone(exe_file.validate_pre_or_post_eds(home_and_eds),
                                 'Validation pre or post EDS')

    def test_existing_but_non_executable_file(self):
        arguments_str = '{} file.exe remaining args'.format(REL_HOME_OPTION)
        (exe_file, remaining_arguments) = sut.parse_as_first_space_separated_part(arguments_str)
        self.assertEqual('remaining args',
                         remaining_arguments,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_eds,
                        'File is expected to exist pre EDS')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.exe')])) as home_and_eds:
            self.assertIsNotNone(exe_file.validate_pre_eds_if_applicable(home_and_eds.home_dir_path),
                                 'Validation pre EDS')
            self.assertIsNone(exe_file.validate_post_eds_if_applicable(home_and_eds.home_dir_path),
                              'Validation post EDS')
            self.assertIsNotNone(exe_file.validate_pre_or_post_eds(home_and_eds),
                                 'Validation pre or post EDS')

            # def test_existing_file(self):
            #     file_reference = sut.rel_home('file.txt')
            #     with home_and_eds_and_test_as_curr_dir(
            #             home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            #         self.assertTrue(file_reference.file_path_pre_eds(home_and_eds.home_dir_path).exists())
            #         self.assertTrue(file_reference.file_path_post_eds(home_and_eds).exists())
            #
            # def test_non_existing_file(self):
            #     file_reference = sut.rel_home('file.txt')
            #     with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            #         self.assertFalse(file_reference.file_path_pre_eds(home_and_eds.home_dir_path).exists())
            #         self.assertFalse(file_reference.file_path_post_eds(home_and_eds).exists())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestRelHome))
    return ret_val


if __name__ == '__main__':
    unittest.main()
