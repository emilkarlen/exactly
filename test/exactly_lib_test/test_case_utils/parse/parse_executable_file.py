import sys
import unittest
from typing import Sequence

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.help_texts.file_ref import REL_symbol_OPTION
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import file_ref_resolvers2
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_with_symbol import StackedFileRef
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    is_any_data_type
from exactly_lib.symbol.data.restrictions.value_restrictions import StringRestriction
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_executable_file as sut
from exactly_lib.test_case_utils.parse.parse_file_ref import path_or_string_reference_restrictions, \
    path_relativity_restriction
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_and_sds_populators as home_or_sds_pop
from exactly_lib_test.test_case_utils.test_resources import relativity_options, \
    pre_or_post_sds_validator as validator_util, executable_file_test_utils as utils
from exactly_lib_test.test_case_utils.test_resources.executable_file_test_utils import RelativityConfiguration, \
    suite_for, \
    ExpectationOnExeFile
from exactly_lib_test.test_resources import string_formatting
from exactly_lib_test.test_resources.files.paths import non_existing_absolute_path
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.list_values import list_value_of_string_constants, \
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
    ret_val.addTest(unittest.makeSuite(TestParseWithSymbols))
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
                 source_after_parse: asrt.ValueAssertion[ParseSource]):
        self.name = name
        self.source = source
        self.expectation = expectation
        self.source_after_parse = source_after_parse


class TestParseValidSyntaxWithoutArguments(unittest.TestCase):
    def test(self):
        cases = [
            Case('absolute_path',
                 source=string_formatting.file_name(sys.executable),
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_refs.absolute_file_name(sys.executable),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=has_remaining_part_of_first_line('arg2'),
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
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=has_remaining_part_of_first_line('"an argument"'),
                 ),
            Case('option_without_tail',
                 source='%s THE_FILE' % file_ref_texts.REL_HOME_CASE_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of(RelOptionType.REL_HOME_CASE, 'THE_FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=has_remaining_part_of_first_line('tail'),
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
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=has_remaining_part_of_first_line('tail arguments'),
                 ),
            Case('test_path_with_option',
                 source='( %s FILE )' % file_ref_texts.REL_HOME_CASE_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=empty_list_value(),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
                 ),
            Case('test_path_with_option_and_arguments',
                 source='( %s FILE arg1 arg2 )' % file_ref_texts.REL_HOME_CASE_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_resolver_value=list_value_of_string_constants(['arg1', 'arg2']),
                     file_resolver_value=file_ref_of_default_relativity('FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=asrt_source.is_at_end_of_line(1),
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
                 source_after_parse=has_remaining_part_of_first_line('tail1 tail2'),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


class TestParseWithSymbols(unittest.TestCase):
    def test(self):
        path_suffix_of_symbol = 'first_path_component'
        file_symbol = NameAndValue('file_symbol',
                                   file_ref_of(RelOptionType.REL_TMP, path_suffix_of_symbol))
        string_symbol = NameAndValue('string_symbol',
                                     'string symbol value')
        a_string_constant = 'a_string_constant'
        reference_of_relativity_symbol = SymbolReference(
            file_symbol.name,
            path_relativity_restriction(
                sut.PARSE_FILE_REF_CONFIGURATION.options.accepted_relativity_variants
            ))
        reference_of_path_symbol = SymbolReference(
            file_symbol.name,
            path_or_string_reference_restrictions(
                sut.PARSE_FILE_REF_CONFIGURATION.options.accepted_relativity_variants
            ))
        reference_of_path_string_symbol_as_path_component = SymbolReference(string_symbol.name,
                                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                                direct=StringRestriction(),
                                                                                indirect=StringRestriction()),
                                                                            )
        reference_of_string_symbol_as_argument = SymbolReference(string_symbol.name,
                                                                 is_any_data_type(),
                                                                 )
        symbols = SymbolTable({
            file_symbol.name: su.container(file_ref_resolvers2.constant(file_symbol.value)),
            string_symbol.name: su.container(string_resolvers.str_constant(string_symbol.value)),
        })
        cases = [
            Case('symbol references in file',
                 source='{rel_symbol_option} {file_symbol} {string_symbol}'.format(
                     file_symbol=file_symbol.name,
                     string_symbol=symbol_reference_syntax_for_name(string_symbol.name),
                     rel_symbol_option=REL_symbol_OPTION,
                 ),
                 expectation=
                 ExpectationOnExeFile(
                     file_resolver_value=StackedFileRef(file_symbol.value,
                                                        PathPartAsFixedPath(string_symbol.value)),
                     expected_symbol_references_of_file=[reference_of_relativity_symbol,
                                                         reference_of_path_string_symbol_as_path_component],
                     argument_resolver_value=empty_list_value(),
                     expected_symbol_references_of_argument=[],
                     symbol_for_value_checks=symbols,
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
                 ),
            Case('symbol references in file  and argument',
                 source=' ( {file_symbol} {a_string_constant} {string_symbol} ) following arg'.format(
                     file_symbol=symbol_reference_syntax_for_name(file_symbol.name),
                     string_symbol=symbol_reference_syntax_for_name(string_symbol.name),
                     a_string_constant=a_string_constant,
                 ),
                 expectation=
                 ExpectationOnExeFile(
                     file_resolver_value=file_symbol.value,
                     expected_symbol_references_of_file=[reference_of_path_symbol],
                     argument_resolver_value=list_value_of_string_constants([
                         a_string_constant,
                         string_symbol.value
                     ]),
                     expected_symbol_references_of_argument=[reference_of_string_symbol_as_argument],
                     symbol_for_value_checks=symbols,
                 ),
                 source_after_parse=has_remaining_part_of_first_line('following arg'),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


class TestParseInvalidSyntaxWithArguments(unittest.TestCase):
    def test_just_begin_delimiter(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource('('))

    def test_empty_executable(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource('( )'))

    def test_missing_end_delimiter(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource('( FILE arg1 arg2'))


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource(file_ref_texts.REL_HOME_CASE_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource('--invalid-option FILE'))


CONFIGURATION_FOR_PYTHON_EXECUTABLE = TestCaseConfiguration(
    sut.PYTHON_EXECUTABLE_OPTION_STRING,
    validation_result=validator_util.expect_passes_all_validations(),
    file_resolver_value=file_refs.absolute_file_name(sys.executable),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE = TestCaseConfiguration(
    string_formatting.file_name(sys.executable),
    validation_result=validator_util.expect_passes_all_validations(),
    file_resolver_value=file_refs.absolute_file_name(sys.executable),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)

_ABSOLUT_PATH_THAT_DOES_NOT_EXIST = str(non_existing_absolute_path('/absolute/path/that/is/expected/to/not/exist'))

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE = TestCaseConfiguration(
    string_formatting.file_name(_ABSOLUT_PATH_THAT_DOES_NOT_EXIST),
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
                                      source=asrt_source.is_at_end_of_line(1),
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
                                      source=has_remaining_part_of_first_line('arg1 -arg2'),
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
                                      source=asrt_source.is_at_end_of_line(1),
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
                                      source=has_remaining_part_of_first_line('arg1 -arg2'),
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
                                      source=asrt_source.is_at_end_of_line(1),
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
                                      source=has_remaining_part_of_first_line('--outside1 outside2'),
                                      validation_result=self.configuration.validation_result,
                                      argument_resolver_value=list_value_of_string_constants(['inside'])))


def configurations() -> Sequence[RelativityConfiguration]:
    all_except_rel_result = set(RelOptionType).difference({RelOptionType.REL_RESULT})

    for_non_default = [
        RelativityConfiguration(relativity_options.conf_rel_any(rel_option_type))
        for rel_option_type in all_except_rel_result
    ]
    return for_non_default + [
        RelativityConfiguration(relativity_options.default_conf_rel_any(RelOptionType.REL_HOME_CASE)),
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
                    expected_source_after_parse=has_remaining_part_of_first_line('remaining args'),
                    expectation_on_exe_file=expectation_on_exe_file,
                    validator_expectation=validator_expectation)

    def test_non_existing_file(self):
        non_existing_file_path = non_existing_absolute_path('/this/file/is/assumed/to/not/exist')
        non_existing_file_path_str = str(non_existing_file_path)
        arguments_str = '{} remaining args'.format(string_formatting.file_name(non_existing_file_path_str))

        expectation_on_exe_file = ExpectationOnExeFile(
            argument_resolver_value=empty_list_value(),
            file_resolver_value=file_refs.absolute_file_name(non_existing_file_path_str),
            expected_symbol_references_of_file=[],
            expected_symbol_references_of_argument=[],
        )
        validator_expectation = validator_util.Expectation(passes_pre_sds=False,
                                                           passes_post_sds=True)

        self._check(arguments_str,
                    expected_source_after_parse=has_remaining_part_of_first_line('remaining args'),
                    expectation_on_exe_file=expectation_on_exe_file,
                    validator_expectation=validator_expectation)

    def _check(self,
               arguments_str: str,
               expected_source_after_parse: asrt.ValueAssertion[ParseSource],
               expectation_on_exe_file: ExpectationOnExeFile,
               validator_expectation: validator_util.Expectation):
        # ARRANGE #
        source = ParseSource(arguments_str)
        # ACT #
        exe_file = sut.parse_from_parse_source(source)
        # ASSERT #
        utils.check_exe_file(self, expectation_on_exe_file, exe_file)
        expected_source_after_parse.apply_with_message(self, source, 'parse source')

        with home_and_sds_with_act_as_curr_dir() as environment:
            validator_util.check(self, exe_file.validator, environment, validator_expectation)


def _parse_and_check(put: unittest.TestCase,
                     case: Case):
    source = ParseSource(case.source)
    ef = sut.parse_from_parse_source(source)
    utils.check_exe_file(put, case.expectation, ef)
    case.source_after_parse.apply_with_message(put, source,
                                               'parse source after parse')


def file_ref_of(rel_option: RelOptionType,
                path_suffix: str) -> FileRef:
    return file_refs.of_rel_option(rel_option, PathPartAsFixedPath(path_suffix))


def file_ref_of_default_relativity(path_suffix: str) -> FileRef:
    return file_refs.of_rel_option(sut.PARSE_FILE_REF_CONFIGURATION.options.default_option,
                                   PathPartAsFixedPath(path_suffix))


def has_remaining_part_of_first_line(remaining_part: str) -> asrt.ValueAssertion[ParseSource]:
    return asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                            remaining_part_of_current_line=asrt.equals(
                                                remaining_part))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
