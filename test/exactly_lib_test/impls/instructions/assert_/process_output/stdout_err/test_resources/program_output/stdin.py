import unittest
from abc import ABC
from typing import Sequence

from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.abstract_syntax import \
    StdoutErrFromProgramAbsStx
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.program_output import \
    configuration
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import MultiSourceExpectation
from exactly_lib_test.impls.types.matcher.test_resources.matchers import ConstantMatcherWithCustomName
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import NoStdinTestSetup, \
    SingleStdinOfProgramTestSetup, MultipleStdinOfProgramTestSetup
from exactly_lib_test.impls.types.string_matcher.test_resources.string_matchers import EqualsConstant
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import \
    StringSourceOfStringAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2, ProcessExecutionArrangement
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramOfPythonInterpreterAbsStx, FullProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.symbol_context import StringMatcherSymbolContext


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        Test_stdin_is_devnull_WHEN_program_do_not_define_stdin(conf),
        Test_stdin_is_contents_of_string_source_WHEN_program_defines_single_stdin(conf),
        Test_stdin_is_concatenation_of_string_sources_WHEN_program_defines_multiple_stdin(conf),
        TestNonEmptyStdinViaExecution(conf),
    ])


class TestStdinCaseBase(configuration.TestCaseBase, ABC):
    def _do_check(self,
                  program: ProgramAbsStx,
                  process_execution_w_stdin_check: ProcessExecutionArrangement,
                  program_symbols: Sequence[SymbolContext],
                  tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                  ):
        # ARRANGE #
        string_matcher_const_true = StringMatcherSymbolContext.of_primitive(
            'CONSTANT_TRUE',
            ConstantMatcherWithCustomName('const true', True),
        )
        symbols = list(program_symbols) + [string_matcher_const_true]
        copy_stdin_and_check_via_matcher = StdoutErrFromProgramAbsStx(
            program,
            string_matcher_const_true.abstract_syntax,
        )

        checker = instruction_check.Checker(self.configuration.parser())
        # ACT & ASSERT #
        checker.check__abs_stx__source_variants(
            self,
            copy_stdin_and_check_via_matcher,
            ArrangementPostAct2(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                tcds=TcdsArrangementPostAct(
                    tcds_contents=tcds_contents
                ),
                process_execution=process_execution_w_stdin_check,
            ),
            MultiSourceExpectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(symbols)
            ),
        )


class Test_stdin_is_devnull_WHEN_program_do_not_define_stdin(TestStdinCaseBase):
    def runTest(self):
        # ARRANGE #
        test_setup = NoStdinTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                self._do_check(
                    pgm_and_args_case.pgm_and_args,
                    test_setup.proc_exe_env__w_stdin_check,
                    pgm_and_args_case.symbols,
                    pgm_and_args_case.tcds,
                )


class Test_stdin_is_contents_of_string_source_WHEN_program_defines_single_stdin(TestStdinCaseBase):
    def runTest(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                self._do_check(
                    test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                    test_setup.proc_exe_env__w_stdin_check,
                    pgm_and_args_case.symbols,
                    pgm_and_args_case.tcds,
                )


class Test_stdin_is_concatenation_of_string_sources_WHEN_program_defines_multiple_stdin(TestStdinCaseBase):
    def runTest(self):
        # ARRANGE #
        test_setup = MultipleStdinOfProgramTestSetup(self, exit_code=0)
        # ACT & ASSERT #
        self._do_check(
            test_setup.program_w_stdin_syntax,
            test_setup.proc_exe_env__w_stdin_check,
            [test_setup.program_symbol],
        )


class TestNonEmptyStdinViaExecution(configuration.TestCaseBase):
    def runTest(self):
        # ARRANGE #
        contents_of_stdin = 'the contents of stdin'
        string_matcher_that_checks_model = StringMatcherSymbolContext.of_primitive(
            'SM_THAT_CHECKS_MODEL',
            EqualsConstant(contents_of_stdin),
        )
        checker = instruction_check.Checker(self.configuration.parser())
        program_that_copies_stdin_to_output = ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
            py_programs.copy_stdin_to__single_line(self.configuration.output_file())
        )
        copy_stdin_and_check_via_matcher = StdoutErrFromProgramAbsStx(
            FullProgramAbsStx(
                program_that_copies_stdin_to_output,
                stdin=StringSourceOfStringAbsStx.of_str(contents_of_stdin, QuoteType.HARD)
            ),
            string_matcher_that_checks_model.abstract_syntax,
        )

        # ACT & ASSERT #
        checker.check__abs_stx__source_variants(
            self,
            copy_stdin_and_check_via_matcher,
            ArrangementPostAct2(
                symbols=string_matcher_that_checks_model.symbol_table,
            ),
            MultiSourceExpectation(
                symbol_usages=string_matcher_that_checks_model.usages_assertion
            ),
        )
