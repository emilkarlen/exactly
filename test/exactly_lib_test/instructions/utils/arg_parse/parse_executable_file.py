import pathlib
import sys
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_executable_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure import relative_path_options as option
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.instructions.test_resources import executable_file_test_utils as utils
from exactly_lib_test.instructions.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.instructions.test_resources.executable_file_test_utils import RelativityConfiguration, suite_for
from exactly_lib_test.test_case_file_structure.test_resources.concrete_path_part import equals_path_part_string
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_or_sds_populator as home_or_sds_pop
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_or_sds_populator import \
    HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulatorForSdsContents
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources import quoting
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.paths import non_existing_absolute_path
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class TestParseValidSyntaxWithoutArguments(unittest.TestCase):
    def test_absolute_path(self):
        ts = TokenStream2(quoting.file_name(sys.executable))
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string(sys.executable).apply_with_message(self,
                                                                   ef.file_reference(symbols).path_suffix(),
                                                                   'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(ts.is_null)

    def test_without_option(self):
        ts = TokenStream2('file arg2')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('file').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self._has_head_with_string(ts, 'arg2')

    def test_relative_file_name_with_space(self):
        ts = TokenStream2('"the file"')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('the file').apply_with_message(self,
                                                               ef.file_reference(symbols).path_suffix(),
                                                               'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')

    def test_relative_file_name_with_space_and_arguments(self):
        ts = TokenStream2('"the file" "an argument"')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('the file').apply_with_message(self,
                                                               ef.file_reference(symbols).path_suffix(),
                                                               'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self._has_head_with_string(ts, 'an argument')

    def test_option_without_tail(self):
        ts = TokenStream2('%s THE_FILE' % option.REL_HOME_OPTION)
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('THE_FILE').apply_with_message(self,
                                                               ef.file_reference(symbols).path_suffix(),
                                                               'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(ts.is_null)

    def test_option_with_tail(self):
        ts = TokenStream2('%s FILE tail' % option.REL_CWD_OPTION)
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')

        self._has_head_with_string(ts, 'tail')

    def _has_head_with_string(self, ts: TokenStream2, expected_head_string: str):
        self.assertFalse(ts.is_null, 'is-null')
        self.assertEqual(expected_head_string,
                         ts.head.string,
                         'head-string')


class TestParseValidSyntaxWithArguments(unittest.TestCase):
    def test_plain_path_without_tail(self):
        ts = TokenStream2('( FILE )')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(ts.is_null)

    def test_plain_path_with_space(self):
        ts = TokenStream2('( "A FILE" )')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('A FILE').apply_with_message(self,
                                                             ef.file_reference(symbols).path_suffix(),
                                                             'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(ts.is_null)

    def test_plain_path_with_tail(self):
        ts = TokenStream2('( FILE ) tail arguments')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertEqual('tail arguments',
                         _remaining_source(ts))

    def test_path_with_option(self):
        ts = TokenStream2('( %s FILE )' % option.REL_HOME_OPTION)
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertFalse(ef.arguments, 'The executable should have no arguments')
        self.assertTrue(ts.is_null)

    def test_path_with_option_and_arguments(self):
        ts = TokenStream2('( %s FILE arg1 arg2 )' % option.REL_HOME_OPTION)
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertEqual(['arg1', 'arg2'],
                         ef.arguments,
                         'Arguments to the executable')
        self.assertTrue(ts.is_null)

    def test_path_without_option_with_arguments(self):
        ts = TokenStream2('( FILE arg1 arg2 )')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertEqual(['arg1', 'arg2'],
                         ef.arguments,
                         'Arguments to the executable')
        self.assertTrue(ts.is_null)

    def test_path_without_option_with_arguments_with_tail(self):
        ts = TokenStream2('( FILE arg1 arg2 arg3 ) tail1 tail2')
        ef = sut.parse(ts)
        symbols = empty_symbol_table()
        equals_path_part_string('FILE').apply_with_message(self,
                                                           ef.file_reference(symbols).path_suffix(),
                                                           'file_reference/path_suffix')
        self.assertEqual(['arg1', 'arg2', 'arg3'],
                         ef.arguments,
                         'Arguments to the executable')
        self.assertEqual('tail1 tail2',
                         _remaining_source(ts),
                         'Remaining arguments')


class TestParseInvalidSyntaxWithArguments(unittest.TestCase):
    def test_just_begin_delimiter(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream2('('))

    def test_empty_executable(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream2('( )'))

    def test_missing_end_delimiter(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream2('( FILE arg1 arg2'))


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream2(option.REL_HOME_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream2('--invalid-option FILE'))


class TestCaseConfiguration:
    def __init__(self,
                 executable: str,
                 file_ref_type_exists_pre_eds: bool,
                 validation_result: validator_util.Expectation):
        self.executable = executable
        self.file_ref_type_exists_pre_eds = file_ref_type_exists_pre_eds
        self.validation_result = validation_result


class TestCaseConfigurationForPythonExecutable(TestCaseConfiguration):
    def __init__(self):
        super().__init__(sut.PYTHON_EXECUTABLE_OPTION_STRING,
                         file_ref_type_exists_pre_eds=True,
                         validation_result=validator_util.expect_passes_all_validations())


class TestCaseConfigurationForAbsolutePathOfExistingExecutableFile(TestCaseConfiguration):
    def __init__(self):
        super().__init__(quoting.file_name(sys.executable),
                         file_ref_type_exists_pre_eds=True,
                         validation_result=validator_util.expect_passes_all_validations())


class TestCaseConfigurationForAbsolutePathOfNonExistingFile(TestCaseConfiguration):
    def __init__(self):
        path_string = str(non_existing_absolute_path('/absolute/path/that/is/expected/to/not/exist'))
        super().__init__(quoting.file_name(path_string),
                         file_ref_type_exists_pre_eds=True,
                         validation_result=validator_util.expect_validation_pre_eds(False))


class ExecutableTestBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: TestCaseConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _arg(self, template: str) -> str:
        return template.format(executable=self.configuration.executable)


class NoParenthesesAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('{executable}')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream2_is_null,
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class NoParenthesesAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('{executable} arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream2_is('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class ParenthesesWithNoArgumentsInsideAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} )')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream2_is_null,
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class ParenthesesWithNoArgumentsInsideAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} ) arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream2_is('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class ParenthesesWithArgumentsInsideAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} inside1 --inside2 )')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream2_is_null,
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=['inside1', '--inside2']))


class ParenthesesWithArgumentsInsideAndWithFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} inside ) --outside1 outside2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=True,
                                      remaining_argument=utils.token_stream2_is('--outside1 outside2'),
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=['inside']))


def suite_for_test_case_configuration(configuration: TestCaseConfiguration) -> unittest.TestSuite:
    cases = [
        NoParenthesesAndNoFollowingArguments,
        NoParenthesesAndFollowingArguments,
        ParenthesesWithNoArgumentsInsideAndNoFollowingArguments,
        ParenthesesWithNoArgumentsInsideAndFollowingArguments,
        ParenthesesWithArgumentsInsideAndNoFollowingArguments,
        ParenthesesWithArgumentsInsideAndWithFollowingArguments,
    ]
    return unittest.TestSuite([
                                  tc(configuration)
                                  for tc in cases
                                  ])


class RelHomeConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(option.REL_HOME_OPTION, True)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForHomeContents(DirContents([file]))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.home_dir_path / file_name


class DefaultConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__('', True)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForHomeContents(DirContents([file]))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.home_dir_path / file_name


class RelActConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(option.REL_ACT_OPTION, False)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForSdsContents(
            sds_populator.act_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.act_dir / file_name


class RelTmpConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(option.REL_TMP_OPTION, False)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForSdsContents(
            sds_populator.tmp_user_dir_contents(DirContents([file])))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.tmp.user_dir / file_name


class RelCwdConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(option.REL_CWD_OPTION, False)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForSdsContents(
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
        arguments = TokenStream2(arguments_str)
        exe_file = sut.parse(arguments)
        self.assertEqual('remaining args',
                         _remaining_source(arguments),
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_sds(empty_symbol_table()),
                        'File is expected to exist pre SDS')
        with home_and_sds_with_act_as_curr_dir(
                home_dir_contents=DirContents([])) as environment:
            self.assertEqual(sys.executable,
                             exe_file.path_string(environment),
                             'Path string')
            validator_util.check(self, exe_file.validator, environment)

    def test_non_existing_file(self):
        non_existing_file_path = non_existing_absolute_path('/this/file/is/assumed/to/not/exist')
        non_existing_file_path_str = str(non_existing_file_path)
        arguments_str = '{} remaining args'.format(quoting.file_name(non_existing_file_path_str))
        arguments = TokenStream2(arguments_str)
        exe_file = sut.parse(arguments)
        self.assertEqual('remaining args',
                         _remaining_source(arguments),
                         'Remaining arguments')
        self.assertTrue(exe_file.exists_pre_sds(empty_symbol_table()),
                        'File is expected to exist pre SDS')
        with home_and_sds_with_act_as_curr_dir(
                home_dir_contents=DirContents([])) as environment:
            self.assertEqual(non_existing_file_path_str,
                             exe_file.path_string(environment),
                             'Path string')
            validator_util.check(self, exe_file.validator, environment,
                                 passes_pre_sds=False)


def suite() -> unittest.TestSuite:
    test_case_configurations = [
        TestCaseConfigurationForPythonExecutable(),
        TestCaseConfigurationForAbsolutePathOfExistingExecutableFile(),
        TestCaseConfigurationForAbsolutePathOfNonExistingFile(),
    ]
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithoutArguments))
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithArguments))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntaxWithArguments))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestParseAbsolutePath))
    for tc_conf in test_case_configurations:
        ret_val.addTests(suite_for_test_case_configuration(tc_conf))
    ret_val.addTests(suite_for(conf)
                     for conf in configurations())
    return ret_val


def _remaining_source(ts: TokenStream2) -> str:
    return ts.source[ts.position:]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
