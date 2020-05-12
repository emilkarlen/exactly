import sys
import unittest
from typing import List

from exactly_lib.definitions.path import REL_HDS_CASE_OPTION
from exactly_lib.instructions.multi_phase import run as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import path_relativities
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.instructions.multi_phase.test_resources import instruction_embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sub_process_result_check as spr_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext, StringIntConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import \
    multiple, TcdsPopulatorForRelOptionType
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.test_resources import relativity_options
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt, \
    relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import \
    RelativityOptionConfigurationForRelOptionType
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_that_exits_with_value_on_command_line
from exactly_lib_test.test_resources.tcds_and_symbols import tcds_test
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfExecute),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfInterpret),
        unittest.makeSuite(TestProgramViaSymbolReference),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfSource),
        unittest.makeSuite(TestExecuteProgramWithPythonExecutorWithSourceOnCommandLine),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_raise_invalid_instruction_argument_when_invalid_quoting(self):
        parser = sut.embryo_parser('instruction-name')
        source = remaining_source('"abc xyz')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestCaseBase(tcds_test.TestCaseBase):
    def _check_single_line_arguments_with_source_variants(self,
                                                          instruction_argument: str,
                                                          arrangement: ArrangementWithSds,
                                                          expectation: embryo_check.Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            parser = sut.embryo_parser('instruction-name')
            embryo_check.check(self, parser, source, arrangement, expectation)


class TestValidationAndSymbolUsagesOfExecute(TestCaseBase):
    def test_validate_should_fail_when_executable_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file'.format(
                relativity_option=relativity_option_conf.option_argument)

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_success_when_executable_does_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} {executable_file}'.format(
                relativity_option=relativity_option_conf.option_argument,
                executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
            )

            expectation = embryo_check.Expectation(
                symbol_usages=asrt.matches_sequence(relativity_option_conf.symbols.usage_expectation_assertions()),
            )

            arrangement = ArrangementWithSds(
                tcds_contents=relativity_option_conf.populator_for_relativity_option_root(
                    fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(option=relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_symbol_references(self):
        python_interpreter_symbol = StringConstantSymbolContext('python_interpreter_symbol', sys.executable)
        execute_program_option_symbol = StringConstantSymbolContext('execute_program_option', '-c')
        exit_code_symbol = StringIntConstantSymbolContext('exit_code_symbol', 5)

        argument = ' {python_interpreter} {execute_program_option} "exit({exit_code})"'.format(
            python_interpreter=python_interpreter_symbol.name__sym_ref_syntax,
            execute_program_option=execute_program_option_symbol.name__sym_ref_syntax,
            exit_code=exit_code_symbol.name__sym_ref_syntax,
        )

        arrangement = ArrangementWithSds(
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                execute_program_option_symbol,
                exit_code_symbol,
            ]),
        )

        expectation = embryo_check.Expectation(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__path_or_string(
                    syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants
                ),
                execute_program_option_symbol.usage_assertion__any_data_type,
                exit_code_symbol.usage_assertion__any_data_type,
            ]),
            main_result=spr_check.is_success_result(exit_code_symbol.int_value, ''),
        )

        parser = sut.embryo_parser('instruction-name')
        following_line = 'following line'
        source = remaining_source(argument, [following_line])
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestValidationAndSymbolUsagesOfInterpret(TestCaseBase):
    def test_success_when_referenced_files_does_exist(self):
        symbol_name_for_executable_file = 'EXECUTABLE_FILE_SYMBOL_NAME'
        symbol_name_for_source_file = 'SOURCE_FILE_SYMBOL_NAME'
        source_file = fs.empty_file('source-file.src')
        for roc_executable_file in relativity_options(symbol_name_for_executable_file):
            for roc_source_file in relativity_options(symbol_name_for_source_file):
                argument = '{relativity_option_executable} {executable_file} {interpret_option}' \
                           ' {relativity_option_source_file} {source_file}'.format(
                    relativity_option_executable=roc_executable_file.option_argument,
                    relativity_option_source_file=roc_source_file.option_argument,
                    executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
                    interpret_option=args.option(syntax_elements.EXISTING_FILE_OPTION_NAME).as_str,
                    source_file=source_file.file_name,
                )

                expectation = embryo_check.Expectation(
                    symbol_usages=asrt.matches_sequence(roc_executable_file.symbols.usage_expectation_assertions() +
                                                        roc_source_file.symbols.usage_expectation_assertions()),
                )

                arrangement = ArrangementWithSds(
                    tcds_contents=multiple([
                        roc_executable_file.populator_for_relativity_option_root(
                            fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                        roc_source_file.populator_for_relativity_option_root(
                            fs.DirContents([source_file])),
                    ]),
                    symbols=SymbolContext.symbol_table_of_contexts(
                        roc_executable_file.symbols.contexts_for_arrangement() +
                        roc_source_file.symbols.contexts_for_arrangement()),

                )
                test_name = 'exe-file-option={}, source-file-option={}'.format(
                    roc_executable_file.test_case_description,
                    roc_source_file.test_case_description,
                )
                with self.subTest(msg=test_name):
                    self._check_single_line_arguments_with_source_variants(argument,
                                                                           arrangement,
                                                                           expectation)

    def test_validate_should_fail_when_executable_does_not_exist(self):
        existing_file_to_interpret = 'existing-file-to-interpret.src'
        home_dir_contents = fs.DirContents([fs.empty_file(existing_file_to_interpret)])
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {interpret_option}' \
                       ' {rel_hds_case_option} {existing_file}'.format(
                relativity_option=relativity_option_conf.option_argument,
                interpret_option=syntax_elements.EXISTING_FILE_OPTION_NAME,
                rel_hds_case_option=REL_HDS_CASE_OPTION,
                existing_file=existing_file_to_interpret,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols.in_arrangement(),
                hds_contents=hds_case_dir_contents(home_dir_contents),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_validate_should_fail_when_file_to_interpret_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '"{python_interpreter}" {interpret_option} {relativity_option} non-existing-file.py'.format(
                python_interpreter=sys.executable,
                interpret_option=args.option(syntax_elements.EXISTING_FILE_OPTION_NAME).as_str,
                relativity_option=relativity_option_conf.option_argument,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_symbol_references(self):
        file_to_interpret = fs.File('python-logic_symbol_utils.py',
                                    python_program_that_exits_with_code_given_as_first_cl_arg)
        file_to_interpret_symbol = StringConstantSymbolContext('file_to_interpret_symbol',
                                                               file_to_interpret.file_name)
        python_interpreter_symbol = StringConstantSymbolContext('python_interpreter_symbol', sys.executable)
        exit_code_symbol = StringIntConstantSymbolContext('exit_code_symbol', 72)

        argument = ' {python_interpreter} {interpret_option} {file_to_interpret}  "{exit_code}"'.format(
            python_interpreter=python_interpreter_symbol.name__sym_ref_syntax,
            interpret_option=args.option(syntax_elements.EXISTING_FILE_OPTION_NAME).as_str,
            file_to_interpret=file_to_interpret_symbol.name__sym_ref_syntax,
            exit_code=exit_code_symbol.name__sym_ref_syntax,
        )

        following_line = 'following line'
        source = remaining_source(argument, [following_line])

        arrangement = ArrangementWithSds(
            tcds_contents=TcdsPopulatorForRelOptionType(
                path_relativities.ALL_REL_OPTIONS_CONFIG.options.default_option,
                fs.DirContents([file_to_interpret])),
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                file_to_interpret_symbol,
                exit_code_symbol,
            ]),
        )

        expectation = embryo_check.Expectation(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__path_or_string(
                    syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants
                ),
                file_to_interpret_symbol.usage_assertion__path_or_string(
                    path_relativities.ALL_REL_OPTIONS_CONFIG.options.accepted_relativity_variants
                ),
                exit_code_symbol.usage_assertion__any_data_type,
            ]),
            main_result=spr_check.is_success_result(exit_code_symbol.int_value, ''),
        )

        parser = sut.embryo_parser('instruction-name')
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestProgramViaSymbolReference(TestCaseBase):
    output_to_stderr = 'on stderr'
    py_file = File('exit-with-value-on-command-line.py',
                   py_pgm_that_exits_with_value_on_command_line(output_to_stderr))

    py_file_rel_opt_conf = relativity_options.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_that_executes_py_pgm_symbol = ProgramSymbolContext.of_sdv(
        'PROGRAM_THAT_EXECUTES_PY_FILE',
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    symbols_dict = program_that_executes_py_pgm_symbol.symbol_table

    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            args.sequence([pgm_args.symbol_ref_command_line(self.program_that_executes_py_pgm_symbol.name),
                           0]).as_str,
            ArrangementWithSds(
                tcds_contents=self.py_file_rel_opt_conf.populator_for_relativity_option_root(
                    DirContents([self.py_file])
                ),
                symbols=self.symbols_dict
            ),
            instruction_embryo_check.Expectation(
                main_result=spr_check.is_success_result(0,
                                                        None),
                symbol_usages=asrt.matches_sequence([
                    self.program_that_executes_py_pgm_symbol.reference_assertion
                ])

            )
        )

    def test_check_non_zero_exit_code(self):
        exit_code = 87
        self._check_single_line_arguments_with_source_variants(
            args.sequence([
                pgm_args.symbol_ref_command_line(self.program_that_executes_py_pgm_symbol.name),
                exit_code
            ]).as_str,
            ArrangementWithSds(
                tcds_contents=self.py_file_rel_opt_conf.populator_for_relativity_option_root(
                    DirContents([self.py_file])
                ),
                symbols=self.symbols_dict
            ),
            instruction_embryo_check.Expectation(
                main_result=spr_check.is_success_result(exit_code,
                                                        self.output_to_stderr),
                symbol_usages=asrt.matches_sequence([
                    self.program_that_executes_py_pgm_symbol.reference_assertion
                ])
            )
        )


class TestValidationAndSymbolUsagesOfSource(TestCaseBase):
    def test_success_when_executable_does_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} {executable_file} {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_argument,
                executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
                source_option=syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
            )

            expectation = embryo_check.Expectation(
                symbol_usages=asrt.matches_sequence(relativity_option_conf.symbols.usage_expectation_assertions()),
            )

            arrangement = ArrangementWithSds(
                tcds_contents=relativity_option_conf.populator_for_relativity_option_root(
                    fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_validate_should_fail_when_executable_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_argument,
                source_option=syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_symbol_references(self):
        python_interpreter_symbol = StringConstantSymbolContext('python_interpreter_symbol', sys.executable)
        execute_program_option_symbol = StringConstantSymbolContext('execute_program_option', '-c')
        exit_code_symbol = StringIntConstantSymbolContext('exit_code_symbol', 87)

        argument = ' {python_interpreter} {execute_program_option} {source_option}   exit({exit_code})  '.format(
            python_interpreter=python_interpreter_symbol.name__sym_ref_syntax,
            execute_program_option=execute_program_option_symbol.name__sym_ref_syntax,
            source_option=syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
            exit_code=exit_code_symbol.name__sym_ref_syntax,
        )

        arrangement = ArrangementWithSds(
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                execute_program_option_symbol,
                exit_code_symbol,
            ]),
        )

        source = remaining_source(argument,
                                  ['following line'])

        expectation = embryo_check.Expectation(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__path_or_string(
                    syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants
                ),
                execute_program_option_symbol.usage_assertion__any_data_type,
                exit_code_symbol.usage_assertion__any_data_type,
            ]),
            main_result=spr_check.is_success_result(exit_code_symbol.int_value, ''),
        )

        parser = sut.embryo_parser('instruction-name')
        embryo_check.check(self, parser, source, arrangement, expectation)


def _expect_validation_error_and_symbol_usages_of(relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration
                                                  ) -> embryo_check.Expectation:
    return _expect_validation_error_and_symbol_usages(relativity_option_conf,
                                                      relativity_option_conf.symbols.usage_expectation_assertions())


def _expect_validation_error_and_symbol_usages(relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration,
                                               expected_symbol_usage: list) -> embryo_check.Expectation:
    expected_symbol_usages_assertion = asrt.matches_sequence(expected_symbol_usage)
    if relativity_option_conf.exists_pre_sds:
        return embryo_check.Expectation(
            validation_pre_sds=IS_VALIDATION_ERROR,
            symbol_usages=expected_symbol_usages_assertion,
        )
    else:
        return embryo_check.Expectation(
            validation_post_sds=IS_VALIDATION_ERROR,
            symbol_usages=expected_symbol_usages_assertion,
        )


class TestExecuteProgramWithPythonExecutorWithSourceOnCommandLine(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            pgm_args.interpret_py_source_line('exit(0)').as_str,
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(0, None)))

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            pgm_args.interpret_py_source_line('exit(1)').as_str,
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(1, '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write("on stderr"); exit(2)'
        self._check_single_line_arguments_with_source_variants(
            pgm_args.interpret_py_source_line(python_program).as_str,
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(2, 'on stderr')))

    def test_non_existing_executable(self):
        self._check_single_line_arguments_with_source_variants(
            '/not/an/executable/program',
            ArrangementWithSds(),
            Expectation(validation_pre_sds=IS_VALIDATION_ERROR))


IS_VALIDATION_ERROR = validation.is_arbitrary_validation_failure()


def relativity_options(symbol_name: str) -> List[RelativityOptionConfigurationForRelOptionType]:
    return [
        rel_opt.default_conf_rel_any(RelOptionType.REL_HDS_CASE),

        rel_opt.conf_rel_any(RelOptionType.REL_ACT),
        rel_opt.conf_rel_any(RelOptionType.REL_TMP),

        rel_opt.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                    symbol_name,
                                    syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants),
        rel_opt.symbol_conf_rel_any(RelOptionType.REL_HDS_CASE,
                                    symbol_name,
                                    syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants),
    ]


RELATIVITY_OPTIONS = relativity_options('EXECUTABLE_FILE_SYMBOL_NAME')

python_program_that_exits_with_code_0 = 'exit(0)'
EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0 = fs.python_executable_file('executable-file',
                                                                   python_program_that_exits_with_code_0)

python_program_that_exits_with_code_given_as_first_cl_arg = """\
import sys

exit_code = int(sys.argv[1])

sys.exit(exit_code)

"""

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
