import pathlib
import sys
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_executable_file as sut
from exactly_lib.instructions.utils.arg_parse import relative_path_options as option
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.instructions.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.instructions.test_resources.executable_file_test_utils import Configuration, suite_for
from exactly_lib_test.test_resources import quoting
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution.utils import home_and_sds_and_test_as_curr_dir
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.paths import non_existing_absolute_path
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe


class TestParseValidSyntaxWithoutArguments(unittest.TestCase):
    def test_absolute_path(self):
        (ef, remaining_arguments) = sut.parse(TokenStream(quoting.file_name(sys.executable)))
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

    def test_relative_file_name_with_space(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('"the file"'))
        self.assertEqual('the file',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')

    def test_relative_file_name_with_space_and_arguments(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('"the file" "an argument"'))
        self.assertEqual('the file',
                         ef.file_reference.file_name)
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertEqual('"an argument"',
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

    def test_plain_path_with_space(self):
        (ef, remaining_arguments) = sut.parse(TokenStream('( "A FILE" )'))
        self.assertEqual('A FILE',
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

    def file_installation(self, file: File) -> (DirContents, sds_populator.SdsPopulator):
        return (DirContents([file]),
                sds_populator.empty())

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.home_dir_path / file_name


class DefaultConfiguration(Configuration):
    def __init__(self):
        super().__init__('', True)

    def file_installation(self, file: File) -> (DirContents, sds_populator.SdsPopulator):
        return (DirContents([file]),
                sds_populator.empty())

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.home_dir_path / file_name


class RelActConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_ACT_OPTION, False)

    def file_installation(self, file: File) -> (DirContents, sds_populator.SdsPopulator):
        return (DirContents([]),
                sds_populator.act_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.act_dir / file_name


class RelTmpConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_TMP_OPTION, False)

    def file_installation(self, file: File) -> (DirContents, sds_populator.SdsPopulator):
        return (DirContents([]),
                sds_populator.tmp_user_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.tmp.user_dir / file_name


class RelCwdConfiguration(Configuration):
    def __init__(self):
        super().__init__(option.REL_CWD_OPTION, False)

    def file_installation(self, file: File) -> (DirContents, sds_populator.SdsPopulator):
        return (DirContents([]),
                sds_populator.act_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.act_dir / file_name


def configurations() -> list:
    return [
        RelHomeConfiguration(),
        RelActConfiguration(),
        RelTmpConfiguration(),
        RelCwdConfiguration(),
        DefaultConfiguration(),
    ]


class TestParseAbsolutePath(unittest.TestCase):
    def test_existing_file(self):
        arguments_str = py_exe.command_line_for_arguments(['remaining', 'args'])
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_sds,
                        'File is expected to exist pre SDS')
        with home_and_sds_and_test_as_curr_dir(
                home_dir_contents=DirContents([])) as home_and_sds:
            self.assertEqual(sys.executable,
                             exe_file.path_string(home_and_sds),
                             'Path string')
            validator_util.check(self, exe_file.validator, home_and_sds)

    def test_non_existing_file(self):
        non_existing_file_path = non_existing_absolute_path('/this/file/is/assumed/to/not/exist')
        non_existing_file_path_str = str(non_existing_file_path)
        arguments_str = '{} remaining args'.format(quoting.file_name(non_existing_file_path_str))
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_sds,
                        'File is expected to exist pre SDS')
        with home_and_sds_and_test_as_curr_dir(
                home_dir_contents=DirContents([])) as home_and_sds:
            self.assertEqual(non_existing_file_path_str,
                             exe_file.path_string(home_and_sds),
                             'Path string')
            validator_util.check(self, exe_file.validator, home_and_sds,
                                 passes_pre_sds=False)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithoutArguments))
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithArguments))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntaxWithArguments))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestParseAbsolutePath))
    ret_val.addTests(suite_for(conf)
                     for conf in configurations())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
