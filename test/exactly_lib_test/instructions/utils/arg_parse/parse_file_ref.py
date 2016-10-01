import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_file_ref as sut
from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_CWD_OPTION, REL_HOME_OPTION, \
    REL_TMP_OPTION
from exactly_lib.instructions.utils.file_ref import FileRef
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.utils import home_and_eds_and_test_as_curr_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


class TestParsesBase(unittest.TestCase):
    def assert_is_file_that_exists_pre_eds(self,
                                           expected_path: pathlib.Path,
                                           home_and_eds: HomeAndEds,
                                           actual: FileRef):
        self.assertTrue(actual.exists_pre_eds)
        self.assertEqual(actual.file_path_pre_eds(home_and_eds.home_dir_path),
                         expected_path)
        self.assertEqual(actual.file_path_pre_or_post_eds(home_and_eds),
                         expected_path)

    def assert_is_file_that_does_not_exist_pre_eds(self,
                                                   expected_path: pathlib.Path,
                                                   home_and_eds: HomeAndEds,
                                                   actual: FileRef):
        self.assertFalse(actual.exists_pre_eds)
        self.assertEqual(actual.file_path_post_eds(home_and_eds.eds),
                         expected_path)
        self.assertEqual(actual.file_path_pre_or_post_eds(home_and_eds),
                         expected_path)


class TestParse(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref__list([])

    def test_parse_without_option(self):
        (file_ref, remaining_arguments) = sut.parse_file_ref__list(['FILE NAME', 'arg2'])
        self.assertEquals('FILE NAME',
                          file_ref.file_name)
        self.assertEquals(['arg2'],
                          remaining_arguments)

    def test_parse_with_option(self):
        # ARRANGE #
        arguments = [REL_CWD_OPTION, 'FILE NAME', 'arg3', 'arg4']
        # ACT #
        (file_ref, remaining_arguments) = sut.parse_file_ref__list(arguments)
        # ASSERT #
        self.assertEquals('FILE NAME',
                          file_ref.file_name)
        self.assertEquals(['arg3', 'arg4'],
                          remaining_arguments)

    def test_fail_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref__list([REL_CWD_OPTION])


class TestParsesCorrectValueFromListWithDefaultConfiguration(TestParsesBase):
    def test_rel_home(self):
        (file_reference, _) = sut.parse_file_ref__list([REL_HOME_OPTION, 'file.txt'])
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.home_dir_path / 'file.txt'
            self.assert_is_file_that_exists_pre_eds(expected_path,
                                                    home_and_eds,
                                                    file_reference)

    def test_rel_cwd(self):
        (file_reference, _) = sut.parse_file_ref__list([REL_CWD_OPTION, 'file.txt'])
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            expected_path = home_and_eds.eds.act_dir / 'file.txt'
            self.assert_is_file_that_does_not_exist_pre_eds(expected_path,
                                                            home_and_eds,
                                                            file_reference)

    def test_rel_tmp(self):
        (file_reference, _) = sut.parse_file_ref__list([REL_TMP_OPTION, 'file.txt'])
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.eds.tmp.user_dir / 'file.txt'
            self.assert_is_file_that_does_not_exist_pre_eds(expected_path,
                                                            home_and_eds,
                                                            file_reference)

    def test_absolute(self):
        abs_path = pathlib.Path.cwd().resolve()
        abs_path_str = str(abs_path)
        (file_reference, _) = sut.parse_file_ref__list([abs_path_str])
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self.assert_is_file_that_exists_pre_eds(abs_path,
                                                    home_and_eds,
                                                    file_reference)

    def test_rel_home_is_default(self):
        (file_reference, _) = sut.parse_file_ref__list(['file-in-home-dir.txt'])
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.home_dir_path / 'file-in-home-dir.txt'
            self.assert_is_file_that_exists_pre_eds(expected_path,
                                                    home_and_eds,
                                                    file_reference)


class TestParsesCorrectValueFromListWithCustomConfiguration(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = sut.Configuration({rel_opts.RelOptionType.REL_ACT},
                                                 rel_opts.RelOptionType.REL_ACT,
                                                 'FILE')
        (file_reference, _) = sut.parse_file_ref__list(['file.txt'],
                                                       custom_configuration)
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.eds.act_dir / 'file.txt'
            self.assert_is_file_that_does_not_exist_pre_eds(expected_path,
                                                            home_and_eds,
                                                            file_reference)


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

    def test_fail_when_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream(REL_CWD_OPTION))


class TestParsesCorrectValueFromTokenStreamWithCustomConfiguration(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = sut.Configuration({rel_opts.RelOptionType.REL_ACT},
                                                 rel_opts.RelOptionType.REL_ACT,
                                                 'FILE')
        (file_reference, _) = sut.parse_file_ref(TokenStream('file.txt'),
                                                 custom_configuration)
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.eds.act_dir / 'file.txt'
            self.assert_is_file_that_does_not_exist_pre_eds(expected_path,
                                                            home_and_eds,
                                                            file_reference)


class TestParsesCorrectValueFromTokenStreamWithDefaultConfiguration(TestParsesBase):
    def test_rel_home(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('%s file.txt' % REL_HOME_OPTION))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.home_dir_path / 'file.txt'
            self.assert_is_file_that_exists_pre_eds(expected_path,
                                                    home_and_eds,
                                                    file_reference)

    def test_rel_cwd(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('%s file.txt' % REL_CWD_OPTION))
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            expected_path = home_and_eds.eds.act_dir / 'file.txt'
            self.assert_is_file_that_does_not_exist_pre_eds(expected_path,
                                                            home_and_eds,
                                                            file_reference)

    def test_rel_tmp(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('%s file.txt' % REL_TMP_OPTION))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.eds.tmp.user_dir / 'file.txt'
            self.assert_is_file_that_does_not_exist_pre_eds(expected_path,
                                                            home_and_eds,
                                                            file_reference)

    def test_absolute(self):
        abs_path = pathlib.Path.cwd().resolve()
        abs_path_str = str(abs_path)
        (file_reference, _) = sut.parse_file_ref(TokenStream(abs_path_str))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self.assert_is_file_that_exists_pre_eds(abs_path,
                                                    home_and_eds,
                                                    file_reference)

    def test_rel_home_is_default(self):
        (file_reference, _) = sut.parse_file_ref(TokenStream('file.txt'))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            expected_path = home_and_eds.home_dir_path / 'file.txt'
            self.assert_is_file_that_exists_pre_eds(expected_path,
                                                    home_and_eds,
                                                    file_reference)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromListWithCustomConfiguration))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromListWithDefaultConfiguration))
    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromTokenStreamWithCustomConfiguration))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromTokenStreamWithDefaultConfiguration))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
