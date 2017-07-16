import pathlib
import sys
import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.instructions.utils.arg_parse import parse_executable_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system_values.file_ref import FileRef
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
from exactly_lib_test.type_system_values.test_resources.list_values import list_value_of_string_constants, \
    empty_list_value


def suite() -> unittest.TestSuite:
    test_case_configurations = [
        CONFIGURATION_FOR_PYTHON_EXECUTABLE,
        CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE,
        CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE,
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
                 validation_result: validator_util.Expectation,
                 file_resolver_value: FileRef,
                 expected_symbol_references_of_file: list,
                 expected_symbol_references_of_argument: list,
                 ):
        self.executable = executable
        self.file_resolver_value = file_resolver_value
        self.expected_symbol_references_of_file = expected_symbol_references_of_file
        self.expected_symbol_references_of_argument = expected_symbol_references_of_argument
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
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_refs.absolute_file_name(sys.executable),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('without_option',
                 source='file arg2',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('file'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=has_head_with_string('arg2'),
                 ),
            Case('relative_file_name_with_space',
                 source='"the file"',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('the file'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('relative_file_name_with_space_and_arguments',
                 source='"the file" "an argument"',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('the file'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=has_head_with_string('an argument'),
                 ),
            Case('option_without_tail',
                 source='%s THE_FILE' % file_ref_texts.REL_HOME_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of(RelOptionType.REL_HOME, 'THE_FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('option_with_tail',
                 source='%s FILE tail' % file_ref_texts.REL_CWD_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of(RelOptionType.REL_CWD, 'FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
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
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_plain_path_with_space',
                 source='( "A FILE" )',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('A FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_plain_path_with_tail',
                 source='( FILE ) tail arguments',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=has_remaining_source('tail arguments'),
                 ),
            Case('test_path_with_option',
                 source='( %s FILE )' % file_ref_texts.REL_HOME_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_path_with_option_and_arguments',
                 source='( %s FILE arg1 arg2 )' % file_ref_texts.REL_HOME_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=list_value_of_string_constants(['arg1', 'arg2']),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_path_without_option_with_arguments',
                 source='( FILE arg1 arg2 )',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=list_value_of_string_constants(['arg1', 'arg2']),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 expected_token_stream_after_parse=assert_token_stream(is_null=asrt.is_true),
                 ),
            Case('test_path_without_option_with_arguments_with_tail',
                 source='( FILE arg1 arg2 arg3 ) tail1 tail2',
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=list_value_of_string_constants(['arg1', 'arg2', 'arg3']),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
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


CONFIGURATION_FOR_PYTHON_EXECUTABLE = TestCaseConfiguration(
    sut.PYTHON_EXECUTABLE_OPTION_STRING,
    validation_result=validator_util.expect_passes_all_validations(),
    file_resolver_value=file_refs.absolute_file_name(sys.executable),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE = TestCaseConfiguration(
    quoting.file_name(sys.executable),
    validation_result=validator_util.expect_passes_all_validations(),
    file_resolver_value=file_refs.absolute_file_name(sys.executable),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)

_ABSOLUT_PATH_THAT_DOES_NOT_EXIST = str(non_existing_absolute_path('/absolute/path/that/is/expected/to/not/exist'))

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE = TestCaseConfiguration(
    quoting.file_name(_ABSOLUT_PATH_THAT_DOES_NOT_EXIST),
    validation_result=validator_util.expect_validation_pre_eds(False),
    file_resolver_value=file_refs.absolute_file_name(_ABSOLUT_PATH_THAT_DOES_NOT_EXIST),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)


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
                    utils.Expectation(file_resolver_value=self.configuration.file_resolver_value,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      remaining_argument=utils.token_stream_is_null,
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=empty_list_value()))


class NoParenthesesAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('{executable} arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(file_resolver_value=self.configuration.file_resolver_value,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      remaining_argument=has_remaining_source('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=empty_list_value()))


class ParenthesesWithNoArgumentsInsideAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} )')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(file_resolver_value=self.configuration.file_resolver_value,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      remaining_argument=utils.token_stream_is_null,
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=empty_list_value(),
                                      ))


class ParenthesesWithNoArgumentsInsideAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} ) arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(file_resolver_value=self.configuration.file_resolver_value,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      remaining_argument=has_remaining_source('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=empty_list_value()))


class ParenthesesWithArgumentsInsideAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} inside1 --inside2 )')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(file_resolver_value=self.configuration.file_resolver_value,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      remaining_argument=utils.token_stream_is_null,
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=list_value_of_string_constants(['inside1', '--inside2'])))


class ParenthesesWithArgumentsInsideAndWithFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('( {executable} inside ) --outside1 outside2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(home_or_sds_pop.empty()),
                    utils.Expectation(file_resolver_value=self.configuration.file_resolver_value,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      remaining_argument=has_remaining_source('--outside1 outside2'),
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=list_value_of_string_constants(['inside'])))


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
            argument_resolver_value=empty_list_value(),
            file_resolver_value=file_refs.absolute_file_name(sys.executable),
            expected_symbol_references_of_file=[],
            expected_symbol_references_of_argument=[],
        )

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
            argument_resolver_value=empty_list_value(),
            file_resolver_value=file_refs.absolute_file_name(non_existing_file_path_str),
            expected_symbol_references_of_file=[],
            expected_symbol_references_of_argument=[],
        )
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


def file_ref_of(rel_option: RelOptionType,
                path_suffix: str) -> FileRef:
    return file_refs.of_rel_option(rel_option, PathPartAsFixedPath(path_suffix))


def file_ref_of_default_relativity(path_suffix: str) -> FileRef:
    return file_refs.of_rel_option(sut.PARSE_FILE_REF_CONFIGURATION.options.default_option,
                                   PathPartAsFixedPath(path_suffix))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
