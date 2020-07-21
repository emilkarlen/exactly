import sys
import unittest
from typing import Sequence, List

from exactly_lib.definitions import path as path_texts
from exactly_lib.definitions.path import REL_symbol_OPTION
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import StringRestriction
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse.parse_path import path_relativity_restriction
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file_executable as sut
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators as tcds_pop
from exactly_lib_test.test_case_utils.test_resources import relativity_options, \
    pre_or_post_sds_validator as validator_util, parse_executable_file_executable_cases as utils
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.parse_executable_file_executable_cases import \
    RelativityConfiguration, \
    suite_for, \
    ExpectationOnExeFile
from exactly_lib_test.test_resources import string_formatting
from exactly_lib_test.test_resources.arguments_building import CustomOptionArgument
from exactly_lib_test.test_resources.files.paths import non_existing_absolute_path
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.data.test_resources.list_ddvs import empty_list_ddv


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
                 validation_result: validation.Expectation,
                 path_ddv: PathDdv,
                 expected_symbol_references_of_file: List[SymbolReference],
                 expected_symbol_references_of_argument: List[SymbolReference],
                 ):
        self.executable = executable
        self.path_ddv = path_ddv
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
                 source_after_parse: ValueAssertion[ParseSource]):
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
                     argument_sdv_value=empty_list_ddv(),
                     path_ddv=paths.absolute_file_name(sys.executable),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
                 ),
            Case('without_option',
                 source='file arg2',
                 expectation=
                 ExpectationOnExeFile(
                     argument_sdv_value=empty_list_ddv(),
                     path_ddv=path_of_default_relativity('file'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=has_remaining_part_of_first_line('arg2'),
                 ),
            Case('relative_file_name_with_space',
                 source='"the file"',
                 expectation=
                 ExpectationOnExeFile(
                     argument_sdv_value=empty_list_ddv(),
                     path_ddv=path_of_default_relativity('the file'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
                 ),
            Case('relative_file_name_with_space_and_arguments',
                 source='"the file" "an argument"',
                 expectation=
                 ExpectationOnExeFile(
                     argument_sdv_value=empty_list_ddv(),
                     path_ddv=path_of_default_relativity('the file'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=has_remaining_part_of_first_line('"an argument"'),
                 ),
            Case('option_without_tail',
                 source='%s THE_FILE' % path_texts.REL_HDS_CASE_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_sdv_value=empty_list_ddv(),
                     path_ddv=path_of(RelOptionType.REL_HDS_CASE, 'THE_FILE'),
                     expected_symbol_references_of_file=[],
                     expected_symbol_references_of_argument=[],
                 ),
                 source_after_parse=asrt_source.is_at_end_of_line(1),
                 ),
            Case('option_with_tail',
                 source='%s FILE tail' % path_texts.REL_CWD_OPTION,
                 expectation=
                 ExpectationOnExeFile(
                     argument_sdv_value=empty_list_ddv(),
                     path_ddv=path_of(RelOptionType.REL_CWD, 'FILE'),
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
        file_symbol = ConstantSuffixPathDdvSymbolContext('file_symbol',
                                                         RelOptionType.REL_TMP,
                                                         'first_path_component')
        string_symbol = StringConstantSymbolContext('string_symbol',
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
        symbols = SymbolContext.symbol_table_of_contexts([
            file_symbol,
            string_symbol,
        ])
        cases = [
            Case('symbol references in file',
                 source='{rel_symbol_option} {file_symbol} {string_symbol}'.format(
                     file_symbol=file_symbol.name,
                     string_symbol=symbol_reference_syntax_for_name(string_symbol.name),
                     rel_symbol_option=REL_symbol_OPTION,
                 ),
                 expectation=
                 ExpectationOnExeFile(
                     path_ddv=paths.stacked(file_symbol.ddv,
                                            paths.constant_path_part(string_symbol.str_value)),
                     expected_symbol_references_of_file=[reference_of_relativity_symbol,
                                                         reference_of_path_string_symbol_as_path_component],
                     argument_sdv_value=empty_list_ddv(),
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
            sut.parse_from_parse_source(ParseSource(path_texts.REL_HDS_CASE_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(ParseSource('{} FILE'.format(CustomOptionArgument('invalid-option'))))


CONFIGURATION_FOR_PYTHON_EXECUTABLE = TestCaseConfiguration(
    syntax_elements.PYTHON_EXECUTABLE_OPTION_STRING,
    validation_result=validation.expect_passes_all_validations(),
    path_ddv=paths.absolute_file_name(sys.executable),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE = TestCaseConfiguration(
    string_formatting.file_name(sys.executable),
    validation_result=validation.expect_passes_all_validations(),
    path_ddv=paths.absolute_file_name(sys.executable),
    expected_symbol_references_of_file=[],
    expected_symbol_references_of_argument=[],
)

_ABSOLUT_PATH_THAT_DOES_NOT_EXIST = str(non_existing_absolute_path('/absolute/path/that/is/expected/to/not/exist'))

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE = TestCaseConfiguration(
    string_formatting.file_name(_ABSOLUT_PATH_THAT_DOES_NOT_EXIST),
    validation_result=validation.expect_validation_pre_eds(False),
    path_ddv=paths.absolute_file_name(_ABSOLUT_PATH_THAT_DOES_NOT_EXIST),
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
                    utils.Arrangement(tcds_pop.empty()),
                    utils.Expectation(path_ddv=self.configuration.path_ddv,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      source=asrt_source.is_at_end_of_line(1),
                                      validation_result=self.configuration.validation_result,
                                      argument_sdv_value=empty_list_ddv()))


class NoParenthesesAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = self._arg('{executable} arg1 -arg2')
        utils.check(self,
                    instruction_argument,
                    utils.Arrangement(tcds_pop.empty()),
                    utils.Expectation(path_ddv=self.configuration.path_ddv,
                                      expected_symbol_references_of_file=self.configuration.expected_symbol_references_of_file,
                                      expected_symbol_references_of_argument=self.configuration.expected_symbol_references_of_argument,
                                      source=has_remaining_part_of_first_line('arg1 -arg2'),
                                      validation_result=self.configuration.validation_result,
                                      argument_sdv_value=empty_list_ddv()))


def configurations() -> Sequence[RelativityConfiguration]:
    all_except_rel_result = set(RelOptionType).difference({RelOptionType.REL_RESULT})

    for_non_default = [
        RelativityConfiguration(relativity_options.conf_rel_any(rel_option_type))
        for rel_option_type in all_except_rel_result
    ]
    return for_non_default + [
        RelativityConfiguration(relativity_options.default_conf_rel_any(RelOptionType.REL_HDS_CASE)),
    ]


class TestParseAbsolutePath(unittest.TestCase):
    def test_existing_file(self):
        arguments_str = py_exe.command_line_for_arguments(['remaining', 'args'])
        expectation_on_exe_file = ExpectationOnExeFile(
            argument_sdv_value=empty_list_ddv(),
            path_ddv=paths.absolute_file_name(sys.executable),
            expected_symbol_references_of_file=[],
            expected_symbol_references_of_argument=[],
        )

        validator_expectation = validation.Expectation(passes_pre_sds=True,
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
            argument_sdv_value=empty_list_ddv(),
            path_ddv=paths.absolute_file_name(non_existing_file_path_str),
            expected_symbol_references_of_file=[],
            expected_symbol_references_of_argument=[],
        )
        validator_expectation = validation.Expectation(passes_pre_sds=False,
                                                       passes_post_sds=True)

        self._check(arguments_str,
                    expected_source_after_parse=has_remaining_part_of_first_line('remaining args'),
                    expectation_on_exe_file=expectation_on_exe_file,
                    validator_expectation=validator_expectation)

    def _check(self,
               arguments_str: str,
               expected_source_after_parse: ValueAssertion[ParseSource],
               expectation_on_exe_file: ExpectationOnExeFile,
               validator_expectation: validation.Expectation):
        # ARRANGE #
        source = ParseSource(arguments_str)
        # ACT #
        exe_file = sut.parse_from_parse_source(source)
        # ASSERT #
        utils.check_exe_file(self, expectation_on_exe_file, exe_file)
        expected_source_after_parse.apply_with_message(self, source, 'parse source')

        with tcds_with_act_as_curr_dir() as environment:
            validator_util.check_ddv(self,
                                     ddv_validators.all_of(exe_file.as_command.resolve(environment.symbols).validators),
                                     environment.tcds,
                                     validator_expectation)


def _parse_and_check(put: unittest.TestCase,
                     case: Case):
    source = ParseSource(case.source)
    ef = sut.parse_from_parse_source(source)
    utils.check_exe_file(put, case.expectation, ef)
    case.source_after_parse.apply_with_message(put, source,
                                               'parse source after parse')


def path_of(rel_option: RelOptionType,
            path_suffix: str) -> PathDdv:
    return paths.of_rel_option(rel_option, paths.constant_path_part(path_suffix))


def path_of_default_relativity(path_suffix: str) -> PathDdv:
    return paths.of_rel_option(syntax_elements.REL_OPTION_ARG_CONF.options.default_option,
                               paths.constant_path_part(path_suffix))


def has_remaining_part_of_first_line(remaining_part: str) -> ValueAssertion[ParseSource]:
    return asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                            remaining_part_of_current_line=asrt.equals(
                                                remaining_part))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
