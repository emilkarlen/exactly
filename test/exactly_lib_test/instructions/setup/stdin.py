import unittest
from typing import List

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions import path as path_syntax
from exactly_lib.definitions.instruction_arguments import ASSIGNMENT_OPERATOR
from exactly_lib.definitions.path import REL_HDS_CASE_OPTION_NAME
from exactly_lib.instructions.setup import stdin as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_utils.parse import parse_here_doc_or_path
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.data import path_ddv
from exactly_lib.type_system.data import paths
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, option_syntax
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation, SettingsBuilderAssertionModel
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import argument_list_source, source4
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.symbol.data.test_resources import here_doc_assertion_utils as hd
from exactly_lib_test.symbol.data.test_resources.path import PathSymbolValueContext
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.string import StringSymbolValueContext
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToFile),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToHereDoc),
        unittest.makeSuite(TestFailingInstructionExecution),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        test_cases = [
            source4(''),
            assignment_of('string superfluous-argument'),
            assignment_of('{file_option} {rel_home} file superfluous-argument'.format(
                file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
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
                file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
                rel_option=option_string)
            with self.subTest(msg='Argument ' + instruction_argument):
                for source in equivalent_source_variants__with_source_check(self,
                                                                            assignment_str_of(instruction_argument)):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_succeed_when_syntax_is_correct__string(self):
        parser = sut.Parser()
        for source in equivalent_source_variants__with_source_check(self, assignment_str_of('string')):
            parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_successful_single_last_line(self):
        test_cases = [
            '{file_option} file'.format(
                file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
            ),
            '{file_option} {relativity_option} "file name with space"'.format(
                file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
                relativity_option=option_syntax(REL_HDS_CASE_OPTION_NAME),
            ),
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            for source in equivalent_source_variants__with_source_check(self, assignment_str_of(instruction_argument)):
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
        for rel_opt in accepted_relativity_options:
            with self.subTest(option_string=rel_opt.option_argument):
                self._run(assignment_of('{file_option} {relativity_option} file.txt'.format(
                    file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
                    relativity_option=rel_opt.option_argument),
                    ['following line']),
                    Arrangement(
                        tcds_contents=rel_opt.populator_for_relativity_option_root(DirContents([
                            empty_file('file.txt')])),
                        symbols=rel_opt.symbols.in_arrangement(),
                    ),
                    Expectation(
                        settings_builder=AssertStdinFileIsSetToFile(
                            paths.of_rel_option(rel_opt.relativity,
                                                paths.constant_path_part('file.txt'))),
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
        for rel_opt in accepted_relativity_options:
            with self.subTest(option_string=rel_opt.option_argument):
                self._run(assignment_of('{file_option} {relativity_option} file.txt'.format(
                    file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
                    relativity_option=rel_opt.option_argument),
                    ['following line']),
                    Arrangement(
                        hds_contents=hds_case_dir_contents(
                            DirContents([empty_file('file.txt')])),
                        symbols=rel_opt.symbols.in_arrangement(),
                    ),
                    Expectation(
                        settings_builder=AssertStdinFileIsSetToFile(
                            paths.of_rel_option(RelOptionType.REL_HDS_CASE,
                                                paths.constant_path_part('file.txt'))),
                        symbol_usages=rel_opt.symbols.usages_expectation(),
                        source=is_at_beginning_of_line(2)),
                )


class TestSuccessfulScenariosWithSetStdinToHereDoc(TestCaseBaseForParser):
    def test_doc_without_symbol_references(self):
        content_line_of_here_doc = 'content line of here doc'
        self._run(assignment_of(' <<MARKER  ',
                                [content_line_of_here_doc,
                                 'MARKER',
                                 'following line']),
                  Arrangement(),
                  Expectation(
                      settings_builder=AssertStdinIsSetToContents(
                          string_sdvs.str_constant(hd.contents_str_from_lines([content_line_of_here_doc])),
                      ),
                      source=is_at_beginning_of_line(4)),
                  )

    def test_doc_with_symbol_references(self):
        content_line_of_here_doc_template = 'content line of here doc with {symbol}'
        here_doc_contents_template = hd.contents_str_from_lines([content_line_of_here_doc_template])
        symbol_name = 'symbol_name'
        symbol = NameAndValue('symbol_name', 'the symbol value')
        expected_symbol_references = [
            SymbolReference(symbol.name,
                            is_any_data_type())
        ]
        cases = [
            NameAndValue('string value container',
                         StringSymbolValueContext.of_constant('string symbol value').container
                         ),
            NameAndValue('path value container',
                         PathSymbolValueContext.of_rel_opt_and_suffix(RelOptionType.REL_ACT, 'file-name.txt').container
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._run(assignment_of(' <<MARKER  ',
                                        [content_line_of_here_doc_template.format(
                                            symbol=symbol_reference_syntax_for_name(symbol_name)),
                                            'MARKER',
                                            'following line']),
                          Arrangement(
                              symbols=SymbolTable({
                                  symbol_name: case.value
                              })
                          ),
                          Expectation(
                              settings_builder=AssertStdinIsSetToContents(
                                  parse_string.string_sdv_from_string(
                                      here_doc_contents_template.format(
                                          symbol=symbol_reference_syntax_for_name(symbol_name)))),
                              symbol_usages=equals_symbol_references(expected_symbol_references),
                              source=is_at_beginning_of_line(4)),
                          )


class TestFailingInstructionExecution(TestCaseBaseForParser):
    def test_referenced_file_does_not_exist(self):
        self._run(assignment_of('{file_option} {rel_home} non-existing-file'.format(
            file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
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
            file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
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
            file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
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
            file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
            rel_home=path_syntax.REL_HDS_CASE_OPTION,
        )),
            Arrangement(
                hds_contents=hds_case_dir_contents(DirContents([empty_dir('directory')]))
            ),
            Expectation(pre_validation_result=svh_assertions.is_validation_error(),
                        source=source_is_at_end)
        )


class AssertStdinFileIsSetToFile(ValueAssertionBase):
    def __init__(self,
                 expected_path: path_ddv.PathDdv):
        self._expected_path = expected_path

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        model = value
        assert isinstance(model, SettingsBuilderAssertionModel)  # Type info for IDE
        put.assertIsNone(model.actual.stdin.contents,
                         message_builder.apply('contents should not be set when using file'))
        expected_file_name = self._expected_path.value_of_any_dependency(
            model.environment.path_resolving_environment_pre_or_post_sds.tcds)
        put.assertEqual(expected_file_name,
                        model.actual.stdin.file_name,
                        message_builder.apply('Name of stdin file in Setup Settings'))


class AssertStdinIsSetToContents(ValueAssertionBase):
    def __init__(self,
                 expected_contents_sdv: StringSdv):
        self.expected_contents_sdv = expected_contents_sdv

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        model = value
        assert isinstance(model, SettingsBuilderAssertionModel)  # Type info for IDE
        put.assertIsNone(model.actual.stdin.file_name,
                         message_builder.apply('file name should not be set when using here doc'))
        expected_contents_str = self.expected_contents_sdv.resolve_value_of_any_dependency(
            model.environment.path_resolving_environment_pre_or_post_sds)
        put.assertEqual(expected_contents_str,
                        model.actual.stdin.contents,
                        message_builder.apply('stdin as contents'))


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
