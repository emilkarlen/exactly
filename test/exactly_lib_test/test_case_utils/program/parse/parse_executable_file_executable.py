import sys
import unittest
from typing import Sequence

from exactly_lib.definitions import file_ref as file_ref_texts
from exactly_lib.definitions.file_ref import REL_symbol_OPTION
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_with_symbol import StackedFileRef
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import StringRestriction
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse.parse_file_ref import path_relativity_restriction
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable as sut
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_and_sds_populators as home_or_sds_pop
from exactly_lib_test.test_case_utils.test_resources import relativity_options, \
    pre_or_post_sds_validator as validator_util, parse_executable_file_executable_cases as utils
from exactly_lib_test.test_case_utils.test_resources.parse_executable_file_executable_cases import \
    RelativityConfiguration, \
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
from exactly_lib_test.type_system.data.test_resources.list_values import empty_list_value


def suite() -> unittest.TestSuite:
    test_case_configurations = [
        CONFIGURATION_FOR_PYTHON_EXECUTABLE,
        CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE,
        CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE,
    ]
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithoutArguments))
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


class TestParseWithSymbols(unittest.TestCase):
    def test(self):
        path_suffix_of_symbol = 'first_path_component'
        file_symbol = NameAndValue('file_symbol',
                                   file_ref_of(RelOptionType.REL_TMP, path_suffix_of_symbol))
        string_symbol = NameAndValue('string_symbol',
                                     'string symbol value')
        reference_of_relativity_symbol = SymbolReference(
            file_symbol.name,
            path_relativity_restriction(
                syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants
            ))
        reference_of_path_string_symbol_as_path_component = SymbolReference(string_symbol.name,
                                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                                direct=StringRestriction(),
                                                                                indirect=StringRestriction()),
                                                                            )
        symbols = SymbolTable({
            file_symbol.name: su.container(file_ref_resolvers.constant(file_symbol.value)),
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
                                                        file_refs.constant_path_part(string_symbol.value)),
                     expected_symbol_references_of_file=[reference_of_relativity_symbol,
                                                         reference_of_path_string_symbol_as_path_component],
                     argument_resolver_value=empty_list_value(),
                     expected_symbol_references_of_argument=[],
                     symbol_for_value_checks=symbols,
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
                 ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource(file_ref_texts.REL_HOME_CASE_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource('--invalid-option FILE'))


CONFIGURATION_FOR_PYTHON_EXECUTABLE = TestCaseConfiguration(
    syntax_elements.PYTHON_EXECUTABLE_OPTION_STRING,
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
            validator_util.check(self, exe_file.as_command.validator, environment, validator_expectation)


def _parse_and_check(put: unittest.TestCase,
                     case: Case):
    source = ParseSource(case.source)
    ef = sut.parse_from_parse_source(source)
    utils.check_exe_file(put, case.expectation, ef)
    case.source_after_parse.apply_with_message(put, source,
                                               'parse source after parse')


def file_ref_of(rel_option: RelOptionType,
                path_suffix: str) -> FileRef:
    return file_refs.of_rel_option(rel_option, file_refs.constant_path_part(path_suffix))


def file_ref_of_default_relativity(path_suffix: str) -> FileRef:
    return file_refs.of_rel_option(syntax_elements.REL_OPTION_ARG_CONF.options.default_option,
                                   file_refs.constant_path_part(path_suffix))


def has_remaining_part_of_first_line(remaining_part: str) -> asrt.ValueAssertion[ParseSource]:
    return asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                            remaining_part_of_current_line=asrt.equals(
                                                remaining_part))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
