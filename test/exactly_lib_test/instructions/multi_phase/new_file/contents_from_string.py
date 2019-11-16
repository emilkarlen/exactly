import unittest
from typing import Callable

from exactly_lib.definitions import path as path_texts
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.type_system.data import paths
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.arguments_building import \
    complete_argument_elements, complete_arguments_with_explicit_contents
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    TestCaseBase
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.utils import \
    DISALLOWED_RELATIVITIES, ALLOWED_DST_FILE_RELATIVITIES, ACCEPTED_RELATIVITY_VARIANTS, IS_SUCCESS, just_parse, \
    AN_ALLOWED_DST_FILE_RELATIVITY
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources import arguments as file_maker_args
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources.arguments import \
    here_document_contents_arguments, \
    string_contents_arguments
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as parse_args
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt, value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithConstantContents),
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestParserConsumptionOfSource),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestSuccessfulScenariosWithConstantContents(TestCaseBase):
    def test_contents_from_string(self):
        string_value = 'the_string_value'
        expected_file = fs.File('a-file-name.txt', string_value)
        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            dst_file = PathArgumentWithRelativity(expected_file.file_name,
                                                  rel_opt_conf)
            arguments = complete_argument_elements(dst_file,
                                                   file_maker_args.string_contents_arguments(string_value))
            with self.subTest(relativity_option_string=rel_opt_conf.option_argument,
                              first_line=arguments.first_line):
                self._check(
                    arguments.as_remaining_source,
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_hds=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_sequence,
                        main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                              fs.DirContents([expected_file])),
                    ))

    def test_string_on_separate_line(self):
        # ARRANGE #
        string_value = 'the_string_value'
        expected_file = fs.File('a-file-name.txt', string_value)
        rel_opt_conf = AN_ALLOWED_DST_FILE_RELATIVITY
        dst_file = PathArgumentWithRelativity(expected_file.file_name,
                                              rel_opt_conf)
        arguments = complete_arguments_with_explicit_contents(dst_file,
                                                              parse_args.string_as_elements(string_value),
                                                              with_file_maker_on_separate_line=True)
        # ACT & ASSERT #
        self._check(
            arguments.as_remaining_source,
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                side_effects_on_hds=f_asrt.dir_is_empty(),
                symbol_usages=asrt.is_empty_sequence,
                main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                      fs.DirContents([expected_file])),
            ))

    def test_contents_from_here_doc(self):
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            dst_file = PathArgumentWithRelativity(expected_file.file_name,
                                                  rel_opt_conf)
            arguments = complete_argument_elements(dst_file,
                                                   here_document_contents_arguments([here_doc_line]))
            with self.subTest(relativity_option_string=rel_opt_conf.option_argument,
                              first_line=arguments.first_line):
                self._check(
                    arguments.as_remaining_source,
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_hds=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_sequence,
                        main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                              fs.DirContents([expected_file])),
                    ))

    def test_contents_from_here_doc_on_separate_line(self):
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        rel_opt_conf = AN_ALLOWED_DST_FILE_RELATIVITY
        dst_file = PathArgumentWithRelativity(expected_file.file_name,
                                              rel_opt_conf)
        arguments = complete_arguments_with_explicit_contents(dst_file,
                                                              parse_args.here_document_as_elements([here_doc_line]),
                                                              with_file_maker_on_separate_line=True)
        self._check(
            arguments.as_remaining_source,
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                side_effects_on_hds=f_asrt.dir_is_empty(),
                symbol_usages=asrt.is_empty_sequence,
                main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                      fs.DirContents([expected_file])),
            ))


class TestSymbolReferences(TestCaseBase):
    def test_symbol_reference_in_dst_file_argument(self):
        sub_dir_name = 'sub-dir'
        relativity = RelOptionType.REL_ACT
        symbol = NameAndValue('symbol_name',
                              paths.of_rel_option(relativity,
                                                  paths.constant_path_part(sub_dir_name)))
        expected_symbol_reference = SymbolReference(
            symbol.name,
            parse_path.path_or_string_reference_restrictions(
                ACCEPTED_RELATIVITY_VARIANTS
            ))
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        self._check(
            remaining_source(
                '{symbol_ref}/{file_name} = <<THE_MARKER'.format(
                    symbol_ref=symbol_reference_syntax_for_name(symbol.name),
                    file_name=expected_file.file_name,
                ),
                [here_doc_line,
                 'THE_MARKER']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                symbols=data_symbol_utils.symbol_table_with_single_path_value(
                    symbol.name,
                    symbol.value),
            ),
            Expectation(
                main_result=IS_SUCCESS,
                symbol_usages=equals_symbol_references([expected_symbol_reference]),
                main_side_effects_on_sds=dir_contains_exactly(
                    relativity,
                    fs.DirContents([
                        fs.Dir(sub_dir_name, [expected_file])])),
            ))

    def _test_symbol_reference_in_dst_file_and_contents(
            self,
            symbol_ref_syntax_2_contents_arguments: Callable[[str], ArgumentElements],
            symbol_value_2_expected_contents: Callable[[str], str]
    ):
        sub_dir_name = 'sub-dir'
        relativity = RelOptionType.REL_ACT
        file_symbol = NameAndValue('file_symbol_name',
                                   paths.of_rel_option(relativity,
                                                       paths.constant_path_part(sub_dir_name)))
        contents_symbol = NameAndValue('contents_symbol_name',
                                       'contents symbol value')

        expected_file_symbol_reference = SymbolReference(
            file_symbol.name,
            parse_path.path_or_string_reference_restrictions(
                ACCEPTED_RELATIVITY_VARIANTS))
        expected_contents_symbol_reference = SymbolReference(
            contents_symbol.name,
            is_any_data_type())

        expected_file_contents = symbol_value_2_expected_contents(contents_symbol.value)

        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        expected_symbol_references = [expected_file_symbol_reference,
                                      expected_contents_symbol_reference]

        symbol_table = data_symbol_utils.SymbolTable({
            file_symbol.name: data_symbol_utils.path_constant_container(file_symbol.value),
            contents_symbol.name: data_symbol_utils.string_constant_container(contents_symbol.value),
        })

        contents_arguments = symbol_ref_syntax_2_contents_arguments(
            symbol_reference_syntax_for_name(contents_symbol.name)).as_arguments

        assert isinstance(contents_arguments, Arguments)

        self._check(
            remaining_source(
                '{symbol_ref}/{file_name} {contents}'.format(
                    symbol_ref=symbol_reference_syntax_for_name(file_symbol.name),
                    file_name=expected_file.file_name,
                    contents=contents_arguments.first_line
                ),
                contents_arguments.following_lines),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                symbols=symbol_table,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                symbol_usages=equals_symbol_references(expected_symbol_references),
                main_side_effects_on_sds=dir_contains_exactly(
                    relativity,
                    fs.DirContents([
                        fs.Dir(sub_dir_name, [expected_file])])),
            ))

    def test_symbol_reference_in_file_argument_and_string(self):
        string_value_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return string_value_template.format(symbol=symbol_value)

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> ArgumentElements:
            string_value = string_value_template.format(symbol=syntax)
            unquoted = string_contents_arguments(SOFT_QUOTE_CHAR + string_value + SOFT_QUOTE_CHAR)
            return unquoted

        self._test_symbol_reference_in_dst_file_and_contents(symbol_ref_syntax_2_contents_arguments,
                                                             symbol_value_2_expected_contents)

    def test_symbol_reference_in_file_argument_and_here_document(self):
        here_doc_line_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return here_doc_line_template.format(symbol=symbol_value) + '\n'

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> ArgumentElements:
            return here_document_contents_arguments([
                here_doc_line_template.format(symbol=syntax)
            ])

        self._test_symbol_reference_in_dst_file_and_contents(symbol_ref_syntax_2_contents_arguments,
                                                             symbol_value_2_expected_contents)


ARGUMENTS_CASES = [
    here_document_contents_arguments(['contents line']),
    string_contents_arguments('string_argument')
]


class TestFailingParse(unittest.TestCase):

    def test_path_is_mandatory__with_option(self):
        for argument_elements in ARGUMENTS_CASES:
            arguments = argument_elements.as_arguments
            with self.subTest(arguments.first_line):
                source = remaining_source('{rel_option} {contents}'.format(
                    rel_option=path_texts.REL_ACT_OPTION,
                    contents=arguments.first_line),
                    arguments.following_lines)

                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    just_parse(source)

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_RELATIVITIES:
            for argument_elements in ARGUMENTS_CASES:
                arguments = argument_elements.as_arguments
                for following_lines in [[], ['following line']]:
                    with self.subTest(relativity=str(relativity),
                                      first_line=arguments.first_line,
                                      following_lines=repr(following_lines)):
                        option_conf = conf_rel_any(relativity)
                        source = remaining_source(
                            '{rel_opt} file-name {contents}'.format(rel_opt=option_conf.option_argument,
                                                                    contents=arguments.first_line),
                            arguments.following_lines + following_lines)
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            just_parse(source)

    def test_fail_when_contents_is_missing(self):
        arguments = 'expected-argument = '
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments)
            just_parse(source)

    def test_fail_when_superfluous_arguments(self):
        for argument_elements in ARGUMENTS_CASES:
            arguments = argument_elements.as_arguments
            with self.subTest(arguments.first_line):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    source = remaining_source('expected-argument = {contents} superfluous_argument'.format(
                        contents=arguments.first_line),
                        arguments.following_lines)
                    just_parse(source)


class TestParserConsumptionOfSource(TestCaseBase):
    def test_last_line__contents(self):
        for argument_elements in ARGUMENTS_CASES:
            arguments = argument_elements.as_arguments
            with self.subTest(arguments.first_line):
                self._check(
                    remaining_source(
                        '{file_name} {hd_args}'.format(
                            file_name='a-file-name.txt',
                            hd_args=arguments.first_line,
                        ),
                        arguments.following_lines),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        source=source_is_at_end,
                    ),
                )

    def test_not_last_line__contents(self):
        hd_args = here_document_contents_arguments([]).as_arguments
        self._check(
            remaining_source(
                '{file_name} {hd_args}'.format(
                    file_name='a-file-name.txt',
                    hd_args=hd_args.first_line,
                ),
                hd_args.following_lines + ['following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                source=is_at_beginning_of_line(3),
            ),
        )


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        file_contents_cases = [
            NameAndValue(
                'contents of here doc',
                here_document_contents_arguments(['contents'])
            ),
            NameAndValue(
                'contents of string',
                string_contents_arguments('contents')
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            empty_symbol_table())
