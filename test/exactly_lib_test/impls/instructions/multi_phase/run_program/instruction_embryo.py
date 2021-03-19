import sys
import unittest
from typing import List

from exactly_lib.definitions.path import REL_HDS_CASE_OPTION
from exactly_lib.impls.instructions.multi_phase import run as sut
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_relativities
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, \
    MultiSourceExpectation, Expectation
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args, result_assertions
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import MultipleStdinOfProgramTestSetup, \
    SingleStdinOfProgramTestSetup, NoStdinTestSetup, StdinCheckWithProgramWExitCode0ForSuccess
from exactly_lib_test.impls.types.test_resources import arguments_building as args
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt, \
    relativity_options as rel_opt_conf
from exactly_lib_test.impls.types.test_resources.relativity_options import \
    RelativityOptionConfigurationForRelOptionType
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.tcfs.test_resources.tcds_populators import \
    multiple, TcdsPopulatorForRelOptionType
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_that_exits_with_1st_value_on_command_line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.program.test_resources.symbol_context import ProgramSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext, \
    StringIntConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfExecute),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfInterpret),
        unittest.makeSuite(TestProgramViaSymbolReference),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfSource),
        unittest.makeSuite(TestExecuteProgramWithPythonExecutorWithSourceOnCommandLine),
        unittest.makeSuite(TestStdinIsGivenToCommandExecutor),
        TestNonEmptyStdinViaExecution(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_raise_invalid_instruction_argument_when_invalid_quoting(self):
        # ARRANGE #
        source = remaining_source('"abc xyz')
        # ACT & ASSERT #
        PARSE_CHECKER.check_invalid_arguments(self, source)

    def test_superfluous_arguments(self):
        # ARRANGE #
        source = pgm_args.program_w_superfluous_args().as_remaining_source
        # ACT & ASSERT #
        PARSE_CHECKER.check_invalid_arguments(self, source)


class TestValidationAndSymbolUsagesOfExecute(unittest.TestCase):
    def test_validate_should_fail_when_executable_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file'.format(
                relativity_option=relativity_option_conf.option_argument)

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = Arrangement.phase_agnostic(
                symbols=relativity_option_conf.symbols.in_arrangement(),
                tcds=TcdsArrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                EXECUTION_CHECKER.check__w_source_variants(
                    self,
                    argument,
                    arrangement,
                    expectation)

    def test_success_when_executable_does_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} {executable_file}'.format(
                relativity_option=relativity_option_conf.option_argument,
                executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
            )

            expectation = MultiSourceExpectation.phase_agnostic(
                symbol_usages=asrt.matches_sequence(relativity_option_conf.symbols.usage_expectation_assertions()),
            )

            arrangement = Arrangement.phase_agnostic(
                tcds=TcdsArrangement(
                    tcds_contents=relativity_option_conf.populator_for_relativity_option_root(
                        fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])
                    ),
                ),
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(option=relativity_option_conf.test_case_description):
                EXECUTION_CHECKER.check__w_source_variants(
                    self,
                    argument,
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

        arrangement = Arrangement.phase_agnostic(
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                execute_program_option_symbol,
                exit_code_symbol,
            ]),
            tcds=TcdsArrangement(),
        )

        expectation = Expectation.phase_agnostic(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__path_or_string(
                    syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.accepted_relativity_variants
                ),
                execute_program_option_symbol.usage_assertion__w_str_rendering,
                exit_code_symbol.usage_assertion__w_str_rendering,
            ]),
            main_result=result_assertions.equals(exit_code_symbol.int_value, ''),
        )

        parser = sut.embryo_parser('instruction-name')
        following_line = 'following line'
        source = remaining_source(argument, [following_line])
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestValidationAndSymbolUsagesOfInterpret(unittest.TestCase):
    def test_success_when_referenced_files_does_exist(self):
        symbol_name_for_executable_file = 'EXECUTABLE_FILE_SYMBOL_NAME'
        symbol_name_for_source_file = 'SOURCE_FILE_SYMBOL_NAME'
        source_file = File.empty('source-file.src')
        for roc_executable_file in relativity_options_of_symbol(symbol_name_for_executable_file):
            for roc_source_file in relativity_options_of_symbol(symbol_name_for_source_file):
                argument = '{relativity_option_executable} {executable_file} {interpret_option}' \
                           ' {relativity_option_source_file} {source_file}'.format(
                    relativity_option_executable=roc_executable_file.option_argument,
                    relativity_option_source_file=roc_source_file.option_argument,
                    executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
                    interpret_option=args.option(syntax_elements.EXISTING_FILE_OPTION_NAME).as_str,
                    source_file=source_file.file_name,
                )

                expectation = MultiSourceExpectation.phase_agnostic(
                    symbol_usages=asrt.matches_sequence(roc_executable_file.symbols.usage_expectation_assertions() +
                                                        roc_source_file.symbols.usage_expectation_assertions()),
                )

                arrangement = Arrangement.phase_agnostic(
                    tcds=TcdsArrangement(
                        tcds_contents=multiple([
                            roc_executable_file.populator_for_relativity_option_root(
                                fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                            roc_source_file.populator_for_relativity_option_root(
                                fs.DirContents([source_file])),
                        ]),
                    ),
                    symbols=SymbolContext.symbol_table_of_contexts(
                        roc_executable_file.symbols.contexts_for_arrangement() +
                        roc_source_file.symbols.contexts_for_arrangement()),

                )
                test_name = 'exe-file-option={}, source-file-option={}'.format(
                    roc_executable_file.test_case_description,
                    roc_source_file.test_case_description,
                )
                with self.subTest(msg=test_name):
                    EXECUTION_CHECKER.check__w_source_variants(
                        self,
                        argument,
                        arrangement,
                        expectation)

    def test_validate_should_fail_when_executable_does_not_exist(self):
        existing_file_to_interpret = 'existing-file-to-interpret.src'
        home_dir_contents = fs.DirContents([File.empty(existing_file_to_interpret)])
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {interpret_option}' \
                       ' {rel_hds_case_option} {existing_file}'.format(
                relativity_option=relativity_option_conf.option_argument,
                interpret_option=syntax_elements.EXISTING_FILE_OPTION_NAME,
                rel_hds_case_option=REL_HDS_CASE_OPTION,
                existing_file=existing_file_to_interpret,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = Arrangement.phase_agnostic(
                symbols=relativity_option_conf.symbols.in_arrangement(),
                tcds=TcdsArrangement(
                    hds_contents=hds_case_dir_contents(home_dir_contents),
                ),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                EXECUTION_CHECKER.check__w_source_variants(
                    self,
                    argument,
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

            arrangement = Arrangement.phase_agnostic(
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                EXECUTION_CHECKER.check__w_source_variants(
                    self,
                    argument,
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

        arrangement = Arrangement.phase_agnostic(
            tcds=TcdsArrangement(
                tcds_contents=TcdsPopulatorForRelOptionType(
                    path_relativities.ALL_REL_OPTIONS_ARG_CONFIG.options.default_option,
                    fs.DirContents([file_to_interpret])
                ),
            ),
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                file_to_interpret_symbol,
                exit_code_symbol,
            ]),
        )

        expectation = Expectation.phase_agnostic(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__path_or_string(
                    syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.accepted_relativity_variants
                ),
                file_to_interpret_symbol.usage_assertion__path_or_string(
                    path_relativities.ALL_REL_OPTIONS_ARG_CONFIG.options.accepted_relativity_variants
                ),
                exit_code_symbol.usage_assertion__w_str_rendering,
            ]),
            main_result=result_assertions.equals(exit_code_symbol.int_value,
                                                 ''),
        )

        parser = sut.embryo_parser('instruction-name')
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestProgramViaSymbolReference(unittest.TestCase):
    output_to_stderr = 'on stderr'
    py_file = File('exit-with-value-on-command-line.py',
                   py_pgm_that_exits_with_1st_value_on_command_line(output_to_stderr))

    py_file_rel_opt_conf = relativity_options.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_that_executes_py_pgm_symbol = ProgramSymbolContext.of_sdv(
        'PROGRAM_THAT_EXECUTES_PY_FILE',
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    symbols = program_that_executes_py_pgm_symbol.symbol_table

    def test_check_zero_exit_code(self):
        EXECUTION_CHECKER.check__w_source_variants(
            self,
            args.sequence([pgm_args.symbol_ref_command_line(self.program_that_executes_py_pgm_symbol.name),
                           0]).as_str,
            Arrangement.phase_agnostic(
                tcds=TcdsArrangement(
                    tcds_contents=self.py_file_rel_opt_conf.populator_for_relativity_option_root(
                        DirContents([self.py_file])
                    ),
                ),
                symbols=self.symbols
            ),
            MultiSourceExpectation.phase_agnostic(
                main_result=result_assertions.equals(0, None),
                symbol_usages=asrt.matches_sequence([
                    self.program_that_executes_py_pgm_symbol.reference_assertion
                ])

            )
        )

    def test_check_non_zero_exit_code(self):
        exit_code = 87
        EXECUTION_CHECKER.check__w_source_variants(
            self,
            args.sequence([
                pgm_args.symbol_ref_command_line(self.program_that_executes_py_pgm_symbol.name),
                exit_code
            ]).as_str,
            Arrangement.phase_agnostic(
                tcds=TcdsArrangement(
                    tcds_contents=self.py_file_rel_opt_conf.populator_for_relativity_option_root(
                        DirContents([self.py_file])
                    ),
                ),
                symbols=self.symbols
            ),
            MultiSourceExpectation.phase_agnostic(
                main_result=result_assertions.equals(exit_code,
                                                     self.output_to_stderr),
                symbol_usages=asrt.matches_sequence([
                    self.program_that_executes_py_pgm_symbol.reference_assertion
                ])
            )
        )


class TestValidationAndSymbolUsagesOfSource(unittest.TestCase):
    def test_success_when_executable_does_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} {executable_file} {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_argument,
                executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
                source_option=syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
            )

            expectation = MultiSourceExpectation.phase_agnostic(
                symbol_usages=asrt.matches_sequence(relativity_option_conf.symbols.usage_expectation_assertions()),
            )

            arrangement = Arrangement.phase_agnostic(
                tcds=TcdsArrangement(
                    tcds_contents=relativity_option_conf.populator_for_relativity_option_root(
                        fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])
                    ),
                ),
                symbols=relativity_option_conf.symbols.in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                EXECUTION_CHECKER.check__w_source_variants(
                    self,
                    argument,
                    arrangement,
                    expectation)

    def test_validate_should_fail_when_executable_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_argument,
                source_option=syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = Arrangement.phase_agnostic(
                symbols=relativity_option_conf.symbols.in_arrangement(),
                tcds=TcdsArrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                EXECUTION_CHECKER.check__w_source_variants(
                    self,
                    argument,
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

        arrangement = Arrangement.phase_agnostic(
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                execute_program_option_symbol,
                exit_code_symbol,
            ]),
            tcds=TcdsArrangement(),
        )

        source = remaining_source(argument,
                                  ['following line'])

        expectation = Expectation.phase_agnostic(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__path_or_string(
                    syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.accepted_relativity_variants
                ),
                execute_program_option_symbol.usage_assertion__w_str_rendering,
                exit_code_symbol.usage_assertion__w_str_rendering,
            ]),
            main_result=result_assertions.equals(exit_code_symbol.int_value, ''),
        )

        parser = sut.embryo_parser('instruction-name')
        embryo_check.check(self, parser, source, arrangement, expectation)


def _expect_validation_error_and_symbol_usages_of(relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration
                                                  ) -> MultiSourceExpectation:
    return _expect_validation_error_and_symbol_usages(relativity_option_conf,
                                                      relativity_option_conf.symbols.usage_expectation_assertions())


def _expect_validation_error_and_symbol_usages(relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration,
                                               expected_symbol_usage: list) -> MultiSourceExpectation:
    expected_symbol_usages_assertion = asrt.matches_sequence(expected_symbol_usage)
    if relativity_option_conf.exists_pre_sds:
        return MultiSourceExpectation.phase_agnostic(
            validation=ValidationAssertions.pre_sds_fails__w_any_msg(),
            symbol_usages=expected_symbol_usages_assertion,
        )
    else:
        return MultiSourceExpectation.phase_agnostic(
            validation=ValidationAssertions.post_sds_fails__w_any_msg(),
            symbol_usages=expected_symbol_usages_assertion,
        )


class TestExecuteProgramWithPythonExecutorWithSourceOnCommandLine(unittest.TestCase):
    def test_check_zero_exit_code(self):
        EXECUTION_CHECKER.check__w_source_variants(
            self,
            pgm_args.interpret_py_source_line('exit(0)').as_str,
            Arrangement.phase_agnostic(
                tcds=TcdsArrangement(),
            ),
            MultiSourceExpectation.phase_agnostic(
                main_result=result_assertions.equals(0, None)
            )
        )

    def test_check_non_zero_exit_code(self):
        EXECUTION_CHECKER.check__w_source_variants(
            self,
            pgm_args.interpret_py_source_line('exit(1)').as_str,
            Arrangement.phase_agnostic(
                tcds=TcdsArrangement(),
            ),
            MultiSourceExpectation.phase_agnostic(
                main_result=result_assertions.equals(1, '')
            )
        )

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write("on stderr"); exit(2)'
        EXECUTION_CHECKER.check__w_source_variants(
            self,
            pgm_args.interpret_py_source_line(python_program).as_str,
            Arrangement.phase_agnostic(
                tcds=TcdsArrangement(),
            ),
            MultiSourceExpectation.phase_agnostic(
                main_result=result_assertions.equals(2, 'on stderr')
            )
        )

    def test_non_existing_executable(self):
        EXECUTION_CHECKER.check__w_source_variants(
            self,
            '/not/an/executable/program',
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                validation=ValidationAssertions.pre_sds_fails__w_any_msg()
            )
        )


class TestStdinIsGivenToCommandExecutor(unittest.TestCase):
    def test_stdin_is_devnull_WHEN_program_do_not_define_stdin(self):
        # ARRANGE #
        test_setup = NoStdinTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                EXECUTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    pgm_and_args_case.pgm_and_args,
                    Arrangement.phase_agnostic(
                        os_services=test_setup.os_services_w_stdin_check,
                        symbols=pgm_and_args_case.symbol_table,
                        tcds=TcdsArrangement(
                            tcds_contents=pgm_and_args_case.tcds,
                        ),
                    ),
                    MultiSourceExpectation.phase_agnostic(
                        symbol_usages=pgm_and_args_case.usages_assertion,
                        main_result=result_assertions.equals(test_setup.exit_code, None)),
                )

    def test_stdin_is_contents_of_string_source_WHEN_program_defines_single_stdin(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                EXECUTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                    Arrangement.phase_agnostic(
                        os_services=test_setup.os_services_w_stdin_check,
                        symbols=pgm_and_args_case.symbol_table,
                        tcds=TcdsArrangement(
                            tcds_contents=pgm_and_args_case.tcds,
                        ),
                    ),
                    MultiSourceExpectation.phase_agnostic(
                        symbol_usages=pgm_and_args_case.usages_assertion,
                        main_result=result_assertions.equals(test_setup.exit_code, None)),
                )

    def test_stdin_is_concatenation_of_string_sources_WHEN_program_defines_multiple_stdin(self):
        # ARRANGE #
        test_setup = MultipleStdinOfProgramTestSetup(self)
        # ACT & ASSERT #
        EXECUTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            test_setup.program_w_stdin_syntax,
            Arrangement.phase_agnostic(
                os_services=test_setup.os_services_w_stdin_check,
                symbols=test_setup.program_symbol.symbol_table,
                tcds=TcdsArrangement(),
            ),
            MultiSourceExpectation.phase_agnostic(
                symbol_usages=test_setup.program_symbol.usages_assertion,
                main_result=result_assertions.equals(test_setup.exit_code, None)),
        )


class TestNonEmptyStdinViaExecution(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        test_setup = StdinCheckWithProgramWExitCode0ForSuccess()
        # ACT & ASSERT #
        EXECUTION_CHECKER.check__abs_stx(
            self,
            test_setup.program_that_checks_stdin__syntax('the contents of stdin'),
            Arrangement.phase_agnostic(
                tcds=TcdsArrangement(
                    tcds_contents=test_setup.tcds_contents,
                ),
            ),
            Expectation.phase_agnostic(
                main_result=result_assertions.equals(
                    test_setup.exit_code_of_successful_application, None
                )
            ),
        )


def relativity_options_of_symbol(symbol_name: str) -> List[RelativityOptionConfigurationForRelOptionType]:
    return [
        rel_opt.default_conf_rel_any(RelOptionType.REL_HDS_CASE),

        rel_opt.conf_rel_any(RelOptionType.REL_ACT),
        rel_opt.conf_rel_any(RelOptionType.REL_TMP),

        rel_opt.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                    symbol_name,
                                    syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.accepted_relativity_variants),
        rel_opt.symbol_conf_rel_any(RelOptionType.REL_HDS_CASE,
                                    symbol_name,
                                    syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.accepted_relativity_variants),
    ]


RELATIVITY_OPTIONS = relativity_options_of_symbol('EXECUTABLE_FILE_SYMBOL_NAME')

python_program_that_exits_with_code_0 = 'exit(0)'
EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0 = fs.python_executable_file('executable-file',
                                                                   python_program_that_exits_with_code_0)

python_program_that_exits_with_code_given_as_first_cl_arg = """\
import sys

exit_code = int(sys.argv[1])

sys.exit(exit_code)

"""

PARSE_CHECKER = parse_checker.Checker(sut.embryo_parser('instruction-name'))
EXECUTION_CHECKER = embryo_check.Checker(sut.embryo_parser('instruction-name'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
