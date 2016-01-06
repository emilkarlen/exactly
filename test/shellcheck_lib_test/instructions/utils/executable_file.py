import pathlib
import sys
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils import executable_file as sut
from shellcheck_lib.instructions.utils import relative_path_options as option
from shellcheck_lib.instructions.utils.parse_utils import TokenStream
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import pre_or_post_eds_validator as validator_util
from shellcheck_lib_test.instructions.test_resources.executable_file_test_utils import Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_structure import DirContents, File


class TestParseValidSyntaxWithoutArguments(unittest.TestCase):
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
        (ef, remaining_arguments) = sut.parse(TokenStream('%s THE_FILE' % option.REL_HOME_OPTION))
        self.assertEqual('THE_FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(remaining_arguments.is_null)

    def test_option_with_tail(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('%s FILE tail' % option.REL_CWD_OPTION))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertEqual('tail',
                         remaining_arguments.source)


class TestParseValidSyntaxWithArguments(unittest.TestCase):
    def test_plain_path_without_tail(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( FILE )'))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(remaining_arguments.is_null)

    def test_plain_path_with_tail(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( FILE ) tail arguments'))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertEquals('tail arguments',
                          remaining_arguments.source)

    def test_path_with_option(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( %s FILE )' % option.REL_HOME_OPTION))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(remaining_arguments.is_null)

    def test_path_with_option_and_arguments(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( %s FILE arg1 arg2 )' % option.REL_HOME_OPTION))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertEquals(['arg1', 'arg2'],
                          ef.arguments,
                          'Arguments to the executable')
        self.assertTrue(remaining_arguments.is_null)

    def test_path_without_option_with_arguments(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( FILE arg1 arg2 )'))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertEquals(['arg1', 'arg2'],
                          ef.arguments,
                          'Arguments to the executable')
        self.assertTrue(remaining_arguments.is_null)

    def test_path_without_option_with_arguments_with_tail(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( FILE arg1 arg2 arg3 ) tail1 tail2'))
        self.assertEqual('FILE',
                         ef.file_reference.file_name)
        self.assertEquals(['arg1', 'arg2', 'arg3'],
                          ef.arguments,
                          'Arguments to the executable')
        self.assertEquals('tail1 tail2',
                          remaining_arguments.source,
                          'Remaining arguments')


class TestParseInvalidSyntaxWithArguments(unittest.TestCase):
    def test_just_begin_delimiter(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream('('))

    def test_empty_executable(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream('( )'))

    def test_missing_end_delimiter(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream('( FILE arg1 arg2'))


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream(option.REL_HOME_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream('--invalid-option FILE'))


class RelHomeConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_HOME_OPTION, True)

    def file_installation(self, file: File) -> (DirContents, eds_populator.EdsPopulator):
        return (DirContents([file]),
                eds_populator.empty())

    def installed_file_path(self,
                            file_name: str,
                            home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.home_dir_path / file_name


class DefaultConfiguration(Configuration):
    def __init__(self):
        super().__init__('', True)

    def file_installation(self, file: File) -> (DirContents, eds_populator.EdsPopulator):
        return (DirContents([file]),
                eds_populator.empty())

    def installed_file_path(self,
                            file_name: str,
                            home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.home_dir_path / file_name


class RelActConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_ACT_OPTION, False)

    def file_installation(self, file: File) -> (DirContents, eds_populator.EdsPopulator):
        return (DirContents([]),
                eds_populator.act_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.eds.act_dir / file_name


class RelTmpConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_TMP_OPTION, False)

    def file_installation(self, file: File) -> (DirContents, eds_populator.EdsPopulator):
        return (DirContents([]),
                eds_populator.tmp_user_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.eds.tmp.user_dir / file_name


class RelCwdConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_CWD_OPTION, False)

    def file_installation(self, file: File) -> (DirContents, eds_populator.EdsPopulator):
        return (DirContents([]),
                eds_populator.act_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.eds.act_dir / file_name


def configurations() -> list:
    return [
        RelHomeConfiguration(),
        RelActConfiguration(),
        RelTmpConfiguration(),
        RelCwdConfiguration(),
        DefaultConfiguration(),
    ]


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
            validator_util.check(self, exe_file.validator, home_and_eds)

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
            validator_util.check(self, exe_file.validator, home_and_eds,
                                 passes_pre_eds=False)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithoutArguments))
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithArguments))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntaxWithArguments))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestAbsolutePath))
    ret_val.addTests(suite_for(conf)
                     for conf in configurations())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
