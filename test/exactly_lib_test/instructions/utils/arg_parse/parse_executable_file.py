import pathlib
import sys
import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.instructions.utils.arg_parse import parse_executable_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib_test.instructions.test_resources import executable_file_test_utils as utils
from exactly_lib_test.instructions.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.instructions.test_resources.executable_file_test_utils import RelativityConfiguration, suite_for, \
    ExpectationOnExeFile
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_and_sds_populators as home_or_sds_pop
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_resources import quoting
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.paths import non_existing_absolute_path
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system_values.test_resources.concrete_path_part import equals_path_part_string


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


class TestCaseConfiguration:
    def __init__(self,
                 executable: str,
                 file_ref_type_exists_pre_eds: bool,
                 validation_result: validator_util.Expectation):
        self.executable = executable
        self.file_ref_type_exists_pre_eds = file_ref_type_exists_pre_eds
        self.validation_result = validation_result


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


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 expectation: ExpectationOnExeFile,
                 expected_token_stream_after_parse: asrt.ValueAssertion):
        self.name = name
        self.source = source
        self.expectation = expectation
        self.expected_token_stream_after_parse = expected_token_stream_after_parse


class TestParseValidSyntaxWithoutArguments(unittest.TestCase):
    def test(self):
        cases = [
            Case('absolute_path',
                 source=quoting.file_name(sys.executable),
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string(sys.executable),
                     arguments=[]),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('without_option',
                 source='file arg2',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('file'),
                     arguments=[]),
                 expected_token_stream_after_parse=has_head_with_string('arg2'),
                 ),
            Case('relative_file_name_with_space',
                 source='"the file"',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('the file'),
                     arguments=[]),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('relative_file_name_with_space_and_arguments',
                 source='"the file" "an argument"',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('the file'),
                     arguments=[]),
                 expected_token_stream_after_parse=has_head_with_string('an argument'),
                 ),
            Case('option_without_tail',
                 source='%s THE_FILE' % file_ref_texts.REL_HOME_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('THE_FILE'),
                     arguments=[]),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('option_with_tail',
                 source='%s FILE tail' % file_ref_texts.REL_CWD_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=[]),
                 expected_token_stream_after_parse=has_head_with_string('tail'),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


class TestParseValidSyntaxWithArguments(unittest.TestCase):
    def test(self):
        cases = [
            Case('test_plain_path_without_tail',
                 source='( FILE )',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=[]),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_plain_path_with_space',
                 source='( "A FILE" )',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('A FILE'),
                     arguments=[]),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_plain_path_with_tail',
                 source='( FILE ) tail arguments',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=[]),
                 expected_token_stream_after_parse=has_remaining_source('tail arguments'),
                 ),
            Case('test_path_with_option',
                 source='( %s FILE )' % file_ref_texts.REL_HOME_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=[]),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_path_with_option_and_arguments',
                 source='( %s FILE arg1 arg2 )' % file_ref_texts.REL_HOME_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=['arg1', 'arg2']),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_path_without_option_with_arguments',
                 source='( FILE arg1 arg2 )',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=['arg1', 'arg2']),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_path_without_option_with_arguments_with_tail',
                 source='( FILE arg1 arg2 arg3 ) tail1 tail2',
                 expectation=
                 ExpectationOnExeFile(
                     path_suffix=equals_path_part_string('FILE'),
                     arguments=['arg1', 'arg2', 'arg3']),
                 expected_token_stream_after_parse=has_remaining_source('tail1 tail2'),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


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
            sut.parse(TokenStream(file_ref_texts.REL_HOME_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(TokenStream('--invalid-option FILE'))


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
                                      remaining_argument=utils.token_stream_is_null,
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class NoParenthesesAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('{executable} arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=has_remaining_source('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class ParenthesesWithNoArgumentsInsideAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} )')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream_is_null,
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class ParenthesesWithNoArgumentsInsideAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} ) arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=has_remaining_source('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=[]))


class ParenthesesWithArgumentsInsideAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} inside1 --inside2 )')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=self.configuration.file_ref_type_exists_pre_eds,
                                      remaining_argument=utils.token_stream_is_null,
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=['inside1', '--inside2']))


class ParenthesesWithArgumentsInsideAndWithFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} inside ) --outside1 outside2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(exists_pre_eds=True,
                                      remaining_argument=has_remaining_source('--outside1 outside2'),
                                      validation_result=self.configuration.validation_result,
                                      arguments_of_exe_file_ref=['inside']))


class RelHomeConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(file_ref_texts.REL_HOME_OPTION, True)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomePopulator(DirContents([file]))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.home_dir_path / file_name


class DefaultConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__('', True)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return HomePopulator(DirContents([file]))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.home_dir_path / file_name


class RelActConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(file_ref_texts.REL_ACT_OPTION, False)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return sds_populator.contents_in(RelSdsOptionType.REL_ACT, DirContents([file]))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.act_dir / file_name


class RelTmpConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(file_ref_texts.REL_TMP_OPTION, False)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return contents_in(RelSdsOptionType.REL_TMP, DirContents([file]))

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        return home_and_sds.sds.tmp.user_dir / file_name


class RelCwdConfiguration(RelativityConfiguration):
    def __init__(self):
        super().__init__(file_ref_texts.REL_CWD_OPTION, False)

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return sds_populator.contents_in(RelSdsOptionType.REL_ACT, DirContents([file]))

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
        expectation_on_exe_file = ExpectationOnExeFile(
            path_suffix=asrt.anything_goes(),
            arguments=[],
            path_string=asrt.equals(sys.executable),
            exists_pre_sds=asrt.is_true)

        validator_expectation = validator_util.Expectation(passes_pre_sds=True,
                                                           passes_post_sds=True)

        self._check(arguments_str,
                    expected_token_stream_after_parse=has_remaining_source('remaining args'),
                    expectation_on_exe_file=expectation_on_exe_file,
                    validator_expectation=validator_expectation)

    def test_non_existing_file(self):
        non_existing_file_path = non_existing_absolute_path('/this/file/is/assumed/to/not/exist')
        non_existing_file_path_str = str(non_existing_file_path)
        arguments_str = '{} remaining args'.format(quoting.file_name(non_existing_file_path_str))

        expectation_on_exe_file = ExpectationOnExeFile(
            path_suffix=asrt.anything_goes(),
            arguments=[],
            path_string=asrt.equals(non_existing_file_path_str),
            exists_pre_sds=asrt.is_true)
        validator_expectation = validator_util.Expectation(passes_pre_sds=False,
                                                           passes_post_sds=True)

        self._check(arguments_str,
                    expected_token_stream_after_parse=has_remaining_source('remaining args'),
                    expectation_on_exe_file=expectation_on_exe_file,
                    validator_expectation=validator_expectation)

    def _check(self,
               arguments_str: str,
               expected_token_stream_after_parse: asrt.ValueAssertion,
               expectation_on_exe_file: ExpectationOnExeFile,
               validator_expectation: validator_util.Expectation):
        # ARRANGE #
        source = TokenStream(arguments_str)
        # ACT #
        exe_file = sut.parse(source)
        # ASSERT #
        utils.check_exe_file(self, expectation_on_exe_file, exe_file)
        expected_token_stream_after_parse.apply_with_message(self, source, 'token_stream')

        with home_and_sds_with_act_as_curr_dir() as environment:
            validator_util.check(self, exe_file.validator, environment, validator_expectation)


def _remaining_source(ts: TokenStream) -> str:
    return ts.source[ts.position:]


def has_remaining_source(expected_remaining_source: str) -> asrt.ValueAssertion:
    return assert_token_stream(is_null=asrt.is_false,
                               remaining_source=asrt.equals(expected_remaining_source))


def has_head_with_string(expected_head_string: str) -> asrt.ValueAssertion:
    return assert_token_stream(is_null=asrt.is_false,
                               head_token=assert_token_string_is(expected_head_string))


def _parse_and_check(put: unittest.TestCase,
                     case: Case):
    ts = TokenStream(case.source)
    ef = sut.parse(ts)
    utils.check_exe_file(put, case.expectation, ef)
    case.expected_token_stream_after_parse.apply_with_message(put, ts,
                                                              'token stream after parse')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
