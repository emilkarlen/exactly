import unittest
from typing import List

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions import path as path_syntax
from exactly_lib.definitions.instruction_arguments import ASSIGNMENT_OPERATOR
from exactly_lib.definitions.path import REL_HDS_CASE_OPTION_NAME
from exactly_lib.impls.instructions.setup import stdin as sut
from exactly_lib.impls.types.string_or_path import parse_string_or_path
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases import setup as setup_phase
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation, SettingsBuilderAssertionModel
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import argument_list_source, source4
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase
from exactly_lib_test.type_val_deps.types.string.test_resources import here_doc_assertion_utils as hd
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.string_model.test_resources import assertions as asrt_string_model


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToFile),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToHereDoc),
        unittest.makeSuite(TestFailingInstructionExecution),
        TestStringModelAsFileShouldRaiseHardErrorWhenFileDoNotExist(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        test_cases = [
            source4(''),
            assignment_of('string superfluous-argument'),
            assignment_of('{file_option} {rel_home} file superfluous-argument'.format(
                file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
                rel_home=path_syntax.REL_HDS_CASE_OPTION,
            )),
            assignment_of('<<MARKER superfluous argument',
                          ['single line',
                           'MARKER']),
            assignment_of('<<MARKER ',
                          ['single line',
                           'NOT_MARKER']),
        ]
        parser = sut.Parser()
        for source in test_cases:
            with self.subTest(msg='first line of source=' + source.remaining_part_of_current_line):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_succeed_when_syntax_is_correct__with_relativity_option(self):
        parser = sut.Parser()
        for rel_option_type in sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_options:
            option_string = long_option_syntax(REL_OPTIONS_MAP[rel_option_type].option_name.long)
            instruction_argument = '{file_option} {rel_option} file'.format(
                file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
                rel_option=option_string)
            with self.subTest(msg='Argument ' + instruction_argument):
                for source in equivalent_source_variants__with_source_check__consume_last_line(self,
                                                                                               assignment_str_of(
                                                                                                   instruction_argument)):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_succeed_when_syntax_is_correct__string(self):
        parser = sut.Parser()
        for source in equivalent_source_variants__with_source_check__consume_last_line(self,
                                                                                       assignment_str_of('string')):
            parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_successful_single_last_line(self):
        test_cases = [
            '{file_option} file'.format(
                file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
            ),
            '{file_option} {relativity_option} "file name with space"'.format(
                file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
                relativity_option=option_syntax(REL_HDS_CASE_OPTION_NAME),
            ),
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            for source in equivalent_source_variants__with_source_check__consume_last_line(self, assignment_str_of(
                    instruction_argument)):
                parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_here_document(self):
        source = assignment_of_list_of_args(['<<MARKER'],
                                            ['single line',
                                             'MARKER',
                                             'following line'])
        sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, source)
        is_at_beginning_of_line(4).apply_with_message(self, source, 'source')


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestSuccessfulScenariosWithSetStdinToFile(TestCaseBaseForParser):
    def test_file__rel_non_hds(self):
        accepted_relativity_options = [
            rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT),
            rel_opt_conf.conf_rel_any(RelOptionType.REL_TMP),
            rel_opt_conf.symbol_conf_rel_any(
                RelOptionType.REL_TMP,
                'SYMBOL',
                sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants),
        ]
        stdin_file = File('stdin.txt', 'contents of stdin / rel non-hds')
        for rel_opt in accepted_relativity_options:
            with self.subTest(option_string=rel_opt.option_argument):
                self._run(assignment_of('{file_option} {relativity_option} {file_name}'.format(
                    file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
                    relativity_option=rel_opt.option_argument,
                    file_name=stdin_file.name),
                    ['following line']),
                    Arrangement(
                        tcds_contents=rel_opt.populator_for_relativity_option_root(DirContents([
                            stdin_file])),
                        symbols=rel_opt.symbols.in_arrangement(),
                    ),
                    Expectation(
                        settings_builder=AssertStdinIsPresentWithContents(
                            stdin_file.contents,
                            may_depend_on_external_resources=True),
                        symbol_usages=rel_opt.symbols.usages_expectation(),
                        source=is_at_beginning_of_line(2)),
                )

    def test_file__rel_hds(self):
        accepted_relativity_options = [
            rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE),
            rel_opt_conf.default_conf_rel_any(RelOptionType.REL_HDS_CASE),
            rel_opt_conf.symbol_conf_rel_any(
                RelOptionType.REL_HDS_CASE,
                'SYMBOL',
                sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants),
        ]
        stdin_file = File('stdin.txt', 'contents of stdin / rel hds')
        for rel_opt in accepted_relativity_options:
            with self.subTest(option_string=rel_opt.option_argument):
                self._run(assignment_of('{file_option} {relativity_option} {file_name}'.format(
                    file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
                    relativity_option=rel_opt.option_argument,
                    file_name=stdin_file.name),
                    ['following line']),
                    Arrangement(
                        hds_contents=hds_case_dir_contents(
                            DirContents([stdin_file])),
                        symbols=rel_opt.symbols.in_arrangement(),
                    ),
                    Expectation(
                        settings_builder=AssertStdinIsPresentWithContents(
                            stdin_file.contents,
                            may_depend_on_external_resources=True),
                        symbol_usages=rel_opt.symbols.usages_expectation(),
                        source=is_at_beginning_of_line(2)),
                )


class TestStringModelAsFileShouldRaiseHardErrorWhenFileDoNotExist(TestCaseBaseForParser):
    def runTest(self):
        # ARRANGE #
        rel_opt = rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT)
        source_for_non_existing_file = assignment_of('{file_option} {relativity_option} non-existing-file.txt'.format(
            file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
            relativity_option=rel_opt.option_argument),
        )
        parser = sut.Parser()
        proc_exe_arrangement = ProcessExecutionArrangement()
        # ACT & ASSERT #
        instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source_for_non_existing_file)
        self.assertIsInstance(instruction, SetupPhaseInstruction)
        with tcds_with_act_as_curr_dir() as path_resolving_environment:
            environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                path_resolving_environment.tcds,
                SymbolTable.empty(),
                proc_exe_arrangement.process_execution_settings,
            )
            instruction_environment = environment_builder.build_post_sds()
            settings_builder = setup_phase.default_settings()

            main_result = instruction.main(instruction_environment,
                                           proc_exe_arrangement.os_services,
                                           settings_builder)

            asrt_sh.is_success().apply_with_message(self, main_result, 'main result')
            actual_stdin = settings_builder.stdin
            self.assertIsInstance(actual_stdin, StringModel, 'stdin should have been set')
            assert actual_stdin is not None

            with self.assertRaises(HardErrorException) as cm:
                path = actual_stdin.as_file

            asrt_text_doc.is_any_text().apply_with_message(self, cm.exception.error,
                                                           'error message')


class TestSuccessfulScenariosWithSetStdinToHereDoc(TestCaseBaseForParser):
    def test_doc_without_symbol_references(self):
        content_line_of_here_doc = 'content line of here doc'
        expected_stdin_contents = hd.contents_str_from_lines([content_line_of_here_doc])
        self._run(assignment_of(' <<MARKER  ',
                                [content_line_of_here_doc,
                                 'MARKER',
                                 'following line']),
                  Arrangement(),
                  Expectation(
                      settings_builder=AssertStdinIsPresentWithContents(
                          expected_stdin_contents,
                          may_depend_on_external_resources=False,
                      ),
                      source=is_at_beginning_of_line(4)),
                  )

    def test_doc_with_symbol_references(self):
        # ARRANGE #
        content_line_of_here_doc_template = 'content line of here doc with {symbol}'
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')
        expected_stdin_contents = hd.contents_str_from_lines([
            content_line_of_here_doc_template.format(symbol=symbol.str_value)
        ])
        expected_symbol_references = asrt.matches_singleton_sequence(
            symbol.reference_assertion__any_data_type
        )
        # ACT & ASSERT #
        self._run(
            assignment_of(' <<MARKER  ',
                          [content_line_of_here_doc_template.format(
                              symbol=symbol.name__sym_ref_syntax),
                              'MARKER',
                              'following line']),
            Arrangement(
                symbols=symbol.symbol_table
            ),
            Expectation(
                settings_builder=AssertStdinIsPresentWithContents(
                    expected_stdin_contents,
                    may_depend_on_external_resources=False),
                symbol_usages=expected_symbol_references,
                source=is_at_beginning_of_line(4)),
        )


class TestFailingInstructionExecution(TestCaseBaseForParser):
    def test_referenced_file_does_not_exist(self):
        self._run(assignment_of('{file_option} {rel_home} non-existing-file'.format(
            file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
            rel_home=path_syntax.REL_HDS_CASE_OPTION,
        )),
            Arrangement(),
            Expectation(pre_validation_result=svh_assertions.is_validation_error(),
                        source=source_is_at_end)
        )

    def test_referenced_file_does_not_exist__rel_symbol(self):
        symbol_rel_opt = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_HDS_CASE,
            'SYMBOL',
            sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
        self._run(assignment_of('{file_option} {relativity_option} file.txt'.format(
            file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
            relativity_option=symbol_rel_opt.option_argument)),
            Arrangement(
                symbols=symbol_rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                pre_validation_result=svh_assertions.is_validation_error(),
                symbol_usages=symbol_rel_opt.symbols.usages_expectation(),
                source=source_is_at_end),
        )

    def test_referenced_file_does_not_exist__rel_symbol__post_sds(self):
        symbol_rel_opt = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_ACT,
            'SYMBOL',
            sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
        self._run(assignment_of('{file_option} {relativity_option} file.txt'.format(
            file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
            relativity_option=symbol_rel_opt.option_argument)),
            Arrangement(
                symbols=symbol_rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                post_validation_result=svh_assertions.is_validation_error(),
                symbol_usages=symbol_rel_opt.symbols.usages_expectation(),
                source=source_is_at_end),
        )

    def test_referenced_file_is_a_directory(self):
        self._run(assignment_of('{file_option} {rel_home} directory'.format(
            file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
            rel_home=path_syntax.REL_HDS_CASE_OPTION,
        )),
            Arrangement(
                hds_contents=hds_case_dir_contents(DirContents([Dir.empty('directory')]))
            ),
            Expectation(pre_validation_result=svh_assertions.is_validation_error(),
                        source=source_is_at_end)
        )


class AssertStdinIsPresentWithContents(ValueAssertionBase[SettingsBuilderAssertionModel]):
    def __init__(self,
                 expected: str,
                 may_depend_on_external_resources: bool
                 ):
        self._expectation = asrt_string_model.model_string_matches(
            asrt.equals(expected),
            asrt.equals(may_depend_on_external_resources),
        )

    def _apply(self,
               put: unittest.TestCase,
               value: SettingsBuilderAssertionModel,
               message_builder: asrt.MessageBuilder,
               ):
        stdin = value.actual.stdin
        put.assertIsNotNone(stdin,
                            message_builder.apply('stdin should be present'))
        self._expectation.apply(put, stdin, message_builder)


def assignment_of_list_of_args(arguments: List[str],
                               following_lines: iter = ()) -> ParseSource:
    return argument_list_source([instruction_arguments.ASSIGNMENT_OPERATOR] + arguments,
                                following_lines)


def assignment_str_of(argument: str) -> str:
    return ASSIGNMENT_OPERATOR + ' ' + argument


def assignment_of(first_line: str,
                  following_lines: list = ()) -> ParseSource:
    return ParseSource(
        instruction_arguments.ASSIGNMENT_OPERATOR + ' ' + '\n'.join([first_line] + list(following_lines)))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
