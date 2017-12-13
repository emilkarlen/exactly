import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources import TestCaseBase, \
    ALLOWED_DST_FILE_RELATIVITIES, IS_SUCCESS, ACCEPTED_RELATIVITY_VARIANTS, just_parse, DISALLOWED_RELATIVITIES
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources import \
    here_document_contents_arguments, InvalidDestinationFileTestCasesData, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.test_resources.relativity_arguments import args_with_rel_ops
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt, value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithConstantContents),
        unittest.makeSuite(TestFailingParseWithContentsFromHereDoc),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestParserConsumptionOfSource),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestSuccessfulScenariosWithConstantContents(TestCaseBase):
    def test_contents_from_here_doc(self):
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    remaining_source(
                        '{rel_opt} {file_name} = <<THE_MARKER'.format(rel_opt=rel_opt_conf.option_string,
                                                                      file_name=expected_file.file_name),
                        [here_doc_line,
                         'THE_MARKER']),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))


class TestSymbolReferences(TestCaseBase):
    def test_symbol_reference_in_dst_file_argument(self):
        sub_dir_name = 'sub-dir'
        relativity = RelOptionType.REL_ACT
        symbol = NameAndValue('symbol_name',
                              file_refs.of_rel_option(relativity,
                                                      PathPartAsFixedPath(sub_dir_name)))
        expected_symbol_reference = SymbolReference(
            symbol.name,
            parse_file_ref.path_or_string_reference_restrictions(
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
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                symbols=data_symbol_utils.symbol_table_with_single_file_ref_value(
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

    def test_symbol_reference_in_file_argument_and_here_document(self):
        sub_dir_name = 'sub-dir'
        relativity = RelOptionType.REL_ACT
        file_symbol = NameAndValue('file_symbol_name',
                                   file_refs.of_rel_option(relativity,
                                                           PathPartAsFixedPath(sub_dir_name)))
        here_doc_symbol = NameAndValue('here_doc_symbol_name',
                                       'here doc symbol value')

        expected_file_symbol_reference = SymbolReference(
            file_symbol.name,
            parse_file_ref.path_or_string_reference_restrictions(
                ACCEPTED_RELATIVITY_VARIANTS))
        expected_here_doc_symbol_reference = SymbolReference(
            here_doc_symbol.name,
            is_any_data_type())

        here_doc_line_template = 'pre symbol {symbol} post symbol'

        expected_file_contents = here_doc_line_template.format(symbol=here_doc_symbol.value) + '\n'

        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        expected_symbol_references = [expected_file_symbol_reference,
                                      expected_here_doc_symbol_reference]

        symbol_table = data_symbol_utils.SymbolTable({
            file_symbol.name: data_symbol_utils.file_ref_constant_container(file_symbol.value),
            here_doc_symbol.name: data_symbol_utils.string_constant_container(here_doc_symbol.value),
        })

        self._check(
            remaining_source(
                '{symbol_ref}/{file_name} = <<THE_MARKER'.format(
                    symbol_ref=symbol_reference_syntax_for_name(file_symbol.name),
                    file_name=expected_file.file_name,
                ),
                [here_doc_line_template.format(
                    symbol=symbol_reference_syntax_for_name(here_doc_symbol.name)),
                    'THE_MARKER']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
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


class TestFailingParseWithContentsFromHereDoc(unittest.TestCase):
    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option} = <<MARKER superfluous ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments,
                                      ['MARKER'])
            just_parse(source)

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_RELATIVITIES:
            for following_lines in [[], ['following line']]:
                with self.subTest(relativity=str(relativity),
                                  following_lines=repr(following_lines)):
                    option_conf = conf_rel_any(relativity)
                    source = remaining_source(
                        '{rel_opt} file-name = <<MARKER'.format(rel_opt=option_conf.option_string),
                        ['MARKER'] + following_lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        just_parse(source)

    def test_fail_when_contents_is_missing(self):
        arguments = 'expected-argument = '
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments)
            just_parse(source)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument = <<MARKER superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments,
                                      ['MARKER'])
            just_parse(source)

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}  expected-argument = <<MARKER superfluous-argument')
        source = remaining_source(arguments,
                                  ['MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(source)


class TestParserConsumptionOfSource(TestCaseBase):
    def test_last_line__contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        hd_args = here_document_contents_arguments([])
        self._check(
            remaining_source(
                '{file_name} {hd_args}'.format(
                    file_name=expected_file.file_name,
                    hd_args=hd_args.first_line,
                ),
                hd_args.following_lines),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                source=source_is_at_end,
            ),
        )

    def test_not_last_line__contents(self):
        expected_file = fs.empty_file('a-file-name.txt')

        hd_args = here_document_contents_arguments([])
        self._check(
            remaining_source(
                '{file_name} {hd_args}'.format(
                    file_name=expected_file.file_name,
                    hd_args=hd_args.first_line,
                ),
                hd_args.following_lines + ['following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
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
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            empty_symbol_table())
