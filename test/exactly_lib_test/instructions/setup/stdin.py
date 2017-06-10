import unittest

from exactly_lib.instructions.setup import stdin as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case_file_structure import file_ref, file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.setup.test_resources.settings_check import Assertion
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.parse_source import source_is_at_end
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir
from exactly_lib_test.test_resources.parse import argument_list_source, source4, remaining_source


class TestParseSet(unittest.TestCase):
    def test_fail(self):
        test_cases = [
            source4(''),
            source4('--rel-home file superfluous-argument'),
            remaining_source('<<MARKER superfluous argument',
                             ['single line',
                              'MARKER'])
        ]
        parser = sut.Parser()
        for source in test_cases:
            with self.subTest(msg='first line of source=' + source.remaining_part_of_current_line):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)

    def test_succeed_when_syntax_is_correct__with_relativity_option(self):
        parser = sut.Parser()
        for rel_option_type in sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_options:
            option_string = long_option_syntax(REL_OPTIONS_MAP[rel_option_type].option_name.long)
            instruction_argument = '{} file'.format(option_string)
            with self.subTest(msg='Argument ' + instruction_argument):
                for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                    parser.parse(source)

    def test_successful_single_line(self):
        test_cases = [
            'file',
            '--rel-home "file name with space"',
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                parser.parse(source)

    def test_here_document(self):
        source = argument_list_source(['<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        sut.Parser().parse(source)
        self.assertFalse(source.has_current_line, 'has_current_line')


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestSuccessfulInstructionExecution(TestCaseBaseForParser):
    def test_file_rel_home__explicitly(self):
        self._run(source4('--rel-home file-in-home-dir.txt'),
                  Arrangement(
                      home_dir_contents=DirContents([
                          empty_file('file-in-home-dir.txt')])
                  ),
                  Expectation(
                      main_side_effects_on_environment=AssertStdinFileIsSetToFile(
                          file_refs.rel_home(PathPartAsFixedPath('file-in-home-dir.txt'))),
                      source=source_is_at_end)
                  )

    def test_file_rel_home__rel_symbol(self):
        symbol_rel_opt = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_TMP,
            'SYMBOL',
            sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
        self._run(source4('{relativity_option} file.txt'.format(
            relativity_option=symbol_rel_opt.option_string)),
            Arrangement(
                home_or_sds_contents=symbol_rel_opt.populator_for_relativity_option_root(DirContents([
                    empty_file('file.txt')])),
                symbols=symbol_rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_side_effects_on_environment=AssertStdinFileIsSetToFile(
                    file_refs.of_rel_option(RelOptionType.REL_TMP,
                                            PathPartAsFixedPath('file.txt'))),
                symbol_usages=symbol_rel_opt.symbols.usages_expectation(),
                source=source_is_at_end),
        )

    def test_file_rel_home__implicitly(self):
        self._run(source4('file-in-home-dir.txt'),
                  Arrangement(home_dir_contents=DirContents([
                      empty_file('file-in-home-dir.txt')])
                  ),
                  Expectation(main_side_effects_on_environment=AssertStdinFileIsSetToFile(
                      file_refs.rel_home(PathPartAsFixedPath('file-in-home-dir.txt'))),
                      source=source_is_at_end)
                  )


class TestFailingInstructionExecution(TestCaseBaseForParser):
    def test_referenced_file_does_not_exist(self):
        self._run(source4('--rel-home non-existing-file'),
                  Arrangement(),
                  Expectation(pre_validation_result=svh_check.is_validation_error(),
                              source=source_is_at_end)
                  )

    def test_referenced_file_does_not_exist__rel_symbol(self):
        symbol_rel_opt = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_HOME,
            'SYMBOL',
            sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
        self._run(source4('{relativity_option} file.txt'.format(
            relativity_option=symbol_rel_opt.option_string)),
            Arrangement(
                symbols=symbol_rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                pre_validation_result=svh_check.is_validation_error(),
                symbol_usages=symbol_rel_opt.symbols.usages_expectation(),
                source=source_is_at_end),
        )

    def test_referenced_file_does_not_exist__rel_symbol__post_sds(self):
        symbol_rel_opt = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_ACT,
            'SYMBOL',
            sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
        self._run(source4('{relativity_option} file.txt'.format(
            relativity_option=symbol_rel_opt.option_string)),
            Arrangement(
                symbols=symbol_rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                post_validation_result=svh_check.is_validation_error(),
                symbol_usages=symbol_rel_opt.symbols.usages_expectation(),
                source=source_is_at_end),
        )

    def test_referenced_file_is_a_directory(self):
        self._run(source4('--rel-home directory'),
                  Arrangement(home_dir_contents=DirContents([
                      empty_dir('directory')])
                  ),
                  Expectation(pre_validation_result=svh_check.is_validation_error(),
                              source=source_is_at_end)
                  )

    def test_single_line_contents_from_here_document(self):
        self._run(argument_list_source(['<<MARKER'],
                                       ['single line',
                                        'MARKER']),
                  Arrangement(),
                  Expectation(main_side_effects_on_environment=AssertStdinIsSetToContents(
                      lines_content(['single line'])),
                      source=source_is_at_end)
                  )


class AssertStdinFileIsSetToFile(Assertion):
    def __init__(self,
                 file_reference: file_ref.FileRef):
        self._file_reference = file_reference

    def apply(self,
              put: unittest.TestCase,
              environment: common.InstructionEnvironmentForPostSdsStep,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        file_path = self._file_reference.value_pre_or_post_sds(
            environment.path_resolving_environment_pre_or_post_sds.home_and_sds)
        put.assertIsNotNone(actual_result.stdin.file_name)
        put.assertEqual(str(file_path),
                        actual_result.stdin.file_name,
                        'Name of stdin file in Setup Settings')


class AssertStdinIsSetToContents(Assertion):
    def __init__(self,
                 contents: str):
        self._contents = contents

    def apply(self,
              put: unittest.TestCase,
              environment: common.InstructionEnvironmentForPostSdsStep,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        put.assertIsNotNone(actual_result.stdin.contents)
        put.assertEqual(self._contents,
                        actual_result.stdin.contents,
                        'Contents of stdin in Setup Settings')


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSet),
        unittest.makeSuite(TestSuccessfulInstructionExecution),
        unittest.makeSuite(TestFailingInstructionExecution),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.main()
